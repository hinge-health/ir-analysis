#!/usr/bin/env python3
"""
Incident Analysis Tool
Extract incident data from Jira and match with Confluence RCA documents
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jira_client import JiraClient
from confluence_client import ConfluenceClient
from rca_analyzer import RCAAnalyzer

def setup_logging():
    """Set up logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    log_file = os.path.join(log_dir, f'incident_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def test_connections(jira_client: JiraClient, confluence_client: ConfluenceClient) -> bool:
    """Test connections to both Jira and Confluence"""
    logger = logging.getLogger(__name__)
    
    logger.info("Testing API connections...")
    
    # Test Jira connection
    if not jira_client.test_connection():
        logger.error("Failed to connect to Jira")
        return False
    
    # Test Confluence connection
    if not confluence_client.test_connection():
        logger.error("Failed to connect to Confluence")
        return False
    
    # Test RCA space access
    if not confluence_client.validate_rca_space_access():
        logger.error("Cannot access RCA documents space")
        return False
    
    logger.info("All connections successful!")
    return True

def match_rca_documents(incidents: List[Dict], confluence_client: ConfluenceClient) -> List[Dict]:
    """Match incidents with their RCA documents"""
    logger = logging.getLogger(__name__)
    
    logger.info("Matching incidents with RCA documents...")
    
    matched_count = 0
    for incident in incidents:
        ticket_key = incident.get('ticket_key')
        
        # First try to use RCA link from Jira comments
        if not incident.get('rca_link'):
            # Search Confluence for RCA document
            rca_url = confluence_client.find_rca_document(ticket_key)
            incident['rca_link'] = rca_url
        
        if incident.get('rca_link'):
            matched_count += 1
    
    logger.info(f"Matched {matched_count}/{len(incidents)} incidents with RCA documents")
    return incidents

def analyze_rca_content(incidents: List[Dict], confluence_client: ConfluenceClient, rca_analyzer: RCAAnalyzer) -> List[Dict]:
    """Analyze RCA document content and extract insights"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting RCA content analysis...")
    
    analyzed_count = 0
    failed_count = 0
    
    for incident in incidents:
        ticket_key = incident.get('ticket_key')
        rca_url = incident.get('rca_link')
        
        # Initialize analysis fields with defaults
        incident['rca_summary'] = 'RCA document not available'
        incident['users_impacted'] = 'Not specified'
        incident['root_causes'] = 'Not analyzed'
        incident['analysis_quality'] = 'N/A'
        
        if not rca_url or rca_url == 'Not Found':
            logger.debug(f"No RCA document available for {ticket_key}")
            continue
        
        try:
            # Retrieve RCA document content
            rca_content_data = confluence_client.get_rca_content(rca_url)
            
            if not rca_content_data:
                logger.warning(f"Could not retrieve RCA content for {ticket_key}")
                incident['rca_summary'] = 'Failed to retrieve RCA content'
                failed_count += 1
                continue
            
            # Clean HTML content for analysis
            cleaned_content = confluence_client.clean_html_content(
                rca_content_data['content_html']
            )
            
            if len(cleaned_content.strip()) < 50:
                logger.warning(f"RCA content too short for analysis: {ticket_key}")
                incident['rca_summary'] = 'RCA content insufficient for analysis'
                failed_count += 1
                continue
            
            # Analyze the content
            analysis_result = rca_analyzer.analyze_rca_document(cleaned_content, ticket_key)
            
            # Update incident with analysis results
            incident['rca_summary'] = analysis_result.incident_summary
            incident['users_impacted'] = analysis_result.users_impacted
            incident['root_causes'] = '; '.join(analysis_result.root_causes)
            incident['analysis_quality'] = analysis_result.analysis_quality
            
            analyzed_count += 1
            logger.debug(f"Successfully analyzed {ticket_key} with {analysis_result.analysis_quality} quality")
            
        except Exception as e:
            logger.error(f"Error analyzing RCA content for {ticket_key}: {str(e)}")
            incident['rca_summary'] = f'Analysis failed: {str(e)}'
            failed_count += 1
    
    logger.info(f"RCA Analysis complete: {analyzed_count} analyzed, {failed_count} failed")
    return incidents

def generate_csv_report(incidents: List[Dict], output_file: str) -> None:
    """Generate CSV report from incident data"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Generating CSV report: {output_file}")
    
    # Prepare data for DataFrame
    report_data = []
    for incident in incidents:
        report_data.append({
            'Ticket Key': incident.get('ticket_key'),
            'Summary': incident.get('summary'),
            'Incident Urgency': incident.get('incident_urgency', 'TBD'),
            'Jira Description': incident.get('description', ''),
            'RCA Link': incident.get('rca_link', 'Not Found'),
            'Pods Engaged': incident.get('pods_engaged', 'TBD'),
            'Created': incident.get('created'),
            'Status': incident.get('status'),
            # New RCA Analysis columns
            'RCA Summary': incident.get('rca_summary', 'Not analyzed'),
            'Users Impacted': incident.get('users_impacted', 'Not specified'),
            'Root Causes': incident.get('root_causes', 'Not analyzed'),
            'Analysis Quality': incident.get('analysis_quality', 'N/A')
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(report_data)
    df.to_csv(output_file, index=False)
    
    logger.info(f"CSV report saved: {output_file}")
    
    # Generate summary statistics
    total_incidents = len(incidents)
    with_rca = len([i for i in incidents if i.get('rca_link') and i.get('rca_link') != 'Not Found'])
    analyzed_rca = len([i for i in incidents if i.get('analysis_quality') and i.get('analysis_quality') != 'N/A'])
    high_quality = len([i for i in incidents if i.get('analysis_quality') == 'high'])
    medium_quality = len([i for i in incidents if i.get('analysis_quality') == 'medium'])
    low_quality = len([i for i in incidents if i.get('analysis_quality') == 'low'])
    
    logger.info(f"Report Summary:")
    logger.info(f"  Total incidents: {total_incidents}")
    logger.info(f"  With RCA documents: {with_rca} ({with_rca/total_incidents*100:.1f}%)")
    logger.info(f"  RCA documents analyzed: {analyzed_rca} ({analyzed_rca/total_incidents*100:.1f}%)")
    logger.info(f"  Analysis quality breakdown: High={high_quality}, Medium={medium_quality}, Low={low_quality}")
    logger.info(f"  Missing RCA documents: {total_incidents - with_rca}")

def main():
    """Main execution function"""
    logger = setup_logging()
    logger.info("Starting Incident Analysis Tool")
    
    try:
        # Initialize clients
        logger.info("Initializing API clients...")
        jira_client = JiraClient()
        confluence_client = ConfluenceClient()
        rca_analyzer = RCAAnalyzer()
        
        # Test connections
        if not test_connections(jira_client, confluence_client):
            logger.error("Connection tests failed. Exiting.")
            return 1
        
        # Get custom field mappings for future reference
        logger.info("Getting custom field mappings...")
        custom_fields = jira_client.get_custom_field_mappings()
        logger.info(f"Custom fields found: {custom_fields}")
        
        # Retrieve incidents from Jira
        logger.info("Retrieving incidents from Jira...")
        incidents = jira_client.get_incidents_since_date('2024-01-01')
        
        if not incidents:
            logger.error("No incidents found!")
            return 1
        
        # Match with RCA documents
        incidents = match_rca_documents(incidents, confluence_client)
        
        # Analyze RCA content
        incidents = analyze_rca_content(incidents, confluence_client, rca_analyzer)
        
        # Generate output
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'incidents_2024_enhanced_{timestamp}.csv')
        
        generate_csv_report(incidents, output_file)
        
        logger.info("Incident analysis completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())