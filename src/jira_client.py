import os
import logging
from typing import List, Dict, Optional
from atlassian import Jira
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

class JiraClient:
    def __init__(self):
        self.jira_url = os.getenv('JIRA_URL')
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        
        if not all([self.jira_url, self.email, self.api_token]):
            raise ValueError("Missing required environment variables. Check JIRA_URL, ATLASSIAN_EMAIL, and ATLASSIAN_API_TOKEN")
        
        self.jira = Jira(
            url=self.jira_url,
            username=self.email,
            password=self.api_token
        )
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> bool:
        """Test connection to Jira"""
        try:
            # Simple test to verify connection
            self.jira.myself()
            self.logger.info("Successfully connected to Jira")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Jira: {str(e)}")
            return False
    
    def get_incidents_since_date(self, start_date: str = '2024-01-01') -> List[Dict]:
        """
        Retrieve all IR incidents since the specified date, excluding duplicates and non-incidents
        
        Args:
            start_date: Date in YYYY-MM-DD format
            
        Returns:
            List of incident dictionaries
        """
        jql = f"project = IR and created > '{start_date}' and status not in (Duplicate, \"Not an Incident\")"
        
        try:
            self.logger.info(f"Executing JQL: {jql}")
            
            # Get all issues using pagination
            incidents = []
            start_at = 0
            max_results = 50
            
            while True:
                response = self.jira.jql(
                    jql=jql,
                    start=start_at,
                    limit=max_results,
                    fields=['key', 'summary', 'description', 'created', 'status', 'comment', 
                           'customfield_11450', 'customfield_11488', 'customfield_11697']
                )
                
                issues = response.get('issues', [])
                if not issues:
                    break
                
                for issue in issues:
                    incident_data = self._extract_incident_data(issue)
                    incidents.append(incident_data)
                
                # Check if we have more results
                total = response.get('total', 0)
                if start_at + max_results >= total:
                    break
                
                start_at += max_results
            
            self.logger.info(f"Retrieved {len(incidents)} incidents")
            return incidents
            
        except Exception as e:
            self.logger.error(f"Error retrieving incidents: {str(e)}")
            raise
    
    def _extract_incident_data(self, issue: Dict) -> Dict:
        """Extract relevant data from a Jira issue"""
        fields = issue.get('fields', {})
        
        # Extract basic fields
        incident_data = {
            'ticket_key': issue.get('key'),
            'summary': fields.get('summary'),
            'description': fields.get('description', ''),
            'created': fields.get('created'),
            'status': fields.get('status', {}).get('name'),
        }
        
        # Extract custom fields
        incident_data.update(self._extract_custom_fields(fields))
        
        # Extract RCA link from comments
        incident_data['rca_link'] = self._find_rca_link_in_comments(fields.get('comment', {}))
        
        return incident_data
    
    def _extract_custom_fields(self, fields: Dict) -> Dict:
        """Extract custom fields like Incident Urgency and Pods Engaged"""
        custom_data = {}
        
        # Extract Incident Urgency (customfield_11450)
        incident_urgency_field = fields.get('customfield_11450')
        if incident_urgency_field:
            if isinstance(incident_urgency_field, dict):
                custom_data['incident_urgency'] = incident_urgency_field.get('value', 'Unknown')
            else:
                custom_data['incident_urgency'] = str(incident_urgency_field)
        else:
            custom_data['incident_urgency'] = 'Not Set'
        
        # Extract Pods Engaged (customfield_11488) - this is the correct field!
        pods_engaged_field = fields.get('customfield_11488')
        if pods_engaged_field:
            if isinstance(pods_engaged_field, list):
                # It's a list of objects with 'value' keys
                pod_names = []
                for pod in pods_engaged_field:
                    if isinstance(pod, dict):
                        pod_names.append(pod.get('value', str(pod)))
                    else:
                        pod_names.append(str(pod))
                custom_data['pods_engaged'] = ', '.join(pod_names)
            elif isinstance(pods_engaged_field, dict):
                custom_data['pods_engaged'] = pods_engaged_field.get('value', 'Unknown')
            else:
                custom_data['pods_engaged'] = str(pods_engaged_field)
        else:
            custom_data['pods_engaged'] = 'Not Set'
        
        # Also extract Pod Responsible (customfield_11697) as additional info
        pod_responsible_field = fields.get('customfield_11697')
        if pod_responsible_field and isinstance(pod_responsible_field, dict):
            responsible_pod = pod_responsible_field.get('value', '')
            if responsible_pod:
                # Add to pods_engaged if not already there
                current_pods = custom_data.get('pods_engaged', '')
                if current_pods == 'Not Set':
                    custom_data['pods_engaged'] = f"Responsible: {responsible_pod}"
                elif responsible_pod not in current_pods:
                    custom_data['pods_engaged'] = f"{current_pods}, Responsible: {responsible_pod}"
        
        return custom_data
    
    def _find_rca_link_in_comments(self, comment_data: Dict) -> Optional[str]:
        """Find RCA document link from Automation for Jira comments"""
        comments = comment_data.get('comments', [])
        
        for comment in comments:
            author = comment.get('author', {})
            author_name = author.get('displayName', '')
            
            if 'Automation for Jira' in author_name:
                body = comment.get('body', '')
                # Look for Confluence RCA links
                if 'RCA' in body and 'hingehealth.atlassian.net/wiki' in body:
                    # Extract the URL - this may need refinement based on actual comment format
                    import re
                    url_pattern = r'https://hingehealth\.atlassian\.net/wiki/[^\s\])]+'
                    match = re.search(url_pattern, body)
                    if match:
                        return match.group(0)
        
        return None
    
    def get_custom_field_mappings(self) -> Dict:
        """Get custom field mappings to identify Incident Urgency and Pods Engaged fields"""
        try:
            fields = self.jira.get_all_fields()
            custom_fields = {}
            
            for field in fields:
                if field.get('custom', False):
                    name = field.get('name', '').lower()
                    field_id = field.get('id')
                    
                    if 'incident urgency' in name or 'urgency' in name:
                        custom_fields['incident_urgency_field'] = field_id
                        self.logger.info(f"Found Incident Urgency field: {field_id}")
                    
                    if 'pods engaged' in name or 'pod' in name:
                        custom_fields['pods_engaged_field'] = field_id
                        self.logger.info(f"Found Pods Engaged field: {field_id}")
            
            return custom_fields
            
        except Exception as e:
            self.logger.error(f"Error getting custom field mappings: {str(e)}")
            return {}