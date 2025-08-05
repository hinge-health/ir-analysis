import os
import logging
from typing import Optional, List, Dict
from atlassian import Confluence
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

class ConfluenceClient:
    def __init__(self):
        self.confluence_url = os.getenv('CONFLUENCE_URL')
        self.email = os.getenv('ATLASSIAN_EMAIL')
        self.api_token = os.getenv('ATLASSIAN_API_TOKEN')
        
        if not all([self.confluence_url, self.email, self.api_token]):
            raise ValueError("Missing required environment variables. Check CONFLUENCE_URL, ATLASSIAN_EMAIL, and ATLASSIAN_API_TOKEN")
        
        self.confluence = Confluence(
            url=self.confluence_url,
            username=self.email,
            password=self.api_token
        )
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # RCA space and path
        self.rca_space = 'RND'
        self.rca_path = 'Incident Response/RCA Documents'
    
    def test_connection(self) -> bool:
        """Test connection to Confluence"""
        try:
            # Simple test to verify connection
            self.confluence.get_all_spaces(start=0, limit=1)
            self.logger.info("Successfully connected to Confluence")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Confluence: {str(e)}")
            return False
    
    def find_rca_document(self, ticket_key: str) -> Optional[str]:
        """
        Find RCA document for a given Jira ticket key
        
        Args:
            ticket_key: Jira ticket key (e.g., 'IR-360')
            
        Returns:
            URL to the RCA document if found, None otherwise
        """
        try:
            # Search for RCA document by title pattern
            search_title = f"RCA {ticket_key}"
            
            # Search in the RND space
            search_results = self.confluence.cql(
                cql=f'space = "{self.rca_space}" AND title ~ "{search_title}"',
                limit=10
            )
            
            results = search_results.get('results', [])
            
            for result in results:
                title = result.get('title', '')
                if title.startswith(f"RCA {ticket_key}"):
                    # Construct the full URL
                    page_id = result.get('id')
                    page_url = f"{self.confluence_url}/pages/viewpage.action?pageId={page_id}"
                    
                    self.logger.info(f"Found RCA document for {ticket_key}: {title}")
                    return page_url
            
            # If not found by title search, try content search
            self.logger.warning(f"RCA document not found by title for {ticket_key}, trying content search")
            return self._search_rca_by_content(ticket_key)
            
        except Exception as e:
            self.logger.error(f"Error searching for RCA document for {ticket_key}: {str(e)}")
            return None
    
    def _search_rca_by_content(self, ticket_key: str) -> Optional[str]:
        """Fallback search for RCA document by content"""
        try:
            # Search for the ticket key in RCA documents
            search_results = self.confluence.cql(
                cql=f'space = "{self.rca_space}" AND text ~ "{ticket_key}" AND title ~ "RCA"',
                limit=10
            )
            
            results = search_results.get('results', [])
            
            for result in results:
                title = result.get('title', '')
                # Check if this looks like an RCA document for our ticket
                if 'RCA' in title and ticket_key in title:
                    page_id = result.get('id')
                    page_url = f"{self.confluence_url}/pages/viewpage.action?pageId={page_id}"
                    
                    self.logger.info(f"Found RCA document by content search for {ticket_key}: {title}")
                    return page_url
            
            self.logger.warning(f"No RCA document found for {ticket_key}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error in content search for {ticket_key}: {str(e)}")
            return None
    
    def get_rca_documents_list(self) -> List[Dict]:
        """
        Get list of all RCA documents in the RCA Documents folder
        
        Returns:
            List of RCA document information
        """
        try:
            # Search for all RCA documents in the space
            search_results = self.confluence.cql(
                cql=f'space = "{self.rca_space}" AND title ~ "RCA IR-"',
                limit=1000  # Increase limit to get all RCA docs
            )
            
            results = search_results.get('results', [])
            rca_docs = []
            
            for result in results:
                title = result.get('title', '')
                page_id = result.get('id')
                page_url = f"{self.confluence_url}/pages/viewpage.action?pageId={page_id}"
                
                # Extract ticket key from title
                import re
                ticket_match = re.search(r'RCA (IR-\d+)', title)
                ticket_key = ticket_match.group(1) if ticket_match else None
                
                rca_docs.append({
                    'title': title,
                    'url': page_url,
                    'ticket_key': ticket_key,
                    'page_id': page_id
                })
            
            self.logger.info(f"Found {len(rca_docs)} RCA documents")
            return rca_docs
            
        except Exception as e:
            self.logger.error(f"Error retrieving RCA documents list: {str(e)}")
            return []
    
    def validate_rca_space_access(self) -> bool:
        """Validate access to the RCA documents space"""
        try:
            # Try to get the RND space
            space = self.confluence.get_space(self.rca_space)
            if space:
                self.logger.info(f"Successfully accessed {self.rca_space} space")
                return True
            else:
                self.logger.error(f"Cannot access {self.rca_space} space")
                return False
                
        except Exception as e:
            self.logger.error(f"Error accessing {self.rca_space} space: {str(e)}")
            return False
    
    def get_rca_content(self, rca_url: str) -> Optional[Dict]:
        """
        Retrieve the full content of an RCA document
        
        Args:
            rca_url: URL to the RCA document
            
        Returns:
            Dictionary with page content and metadata, None if failed
        """
        try:
            # Extract page ID from URL
            # URL formats: 
            # - https://hingehealth.atlassian.net/wiki/pages/viewpage.action?pageId=123456
            # - https://hingehealth.atlassian.net/wiki/spaces/RND/pages/123456/title
            
            if 'pageId=' in rca_url:
                page_id = rca_url.split('pageId=')[1].split('&')[0]
            elif '/pages/' in rca_url:
                # Extract from the /pages/ID/title format
                url_parts = rca_url.split('/pages/')
                if len(url_parts) > 1:
                    # Get the part after /pages/ and extract the numeric ID
                    page_part = url_parts[1].split('/')[0]
                    if page_part.isdigit():
                        page_id = page_part
                    else:
                        self.logger.error(f"Could not extract numeric page ID from URL: {rca_url}")
                        return None
                else:
                    self.logger.error(f"Could not extract page ID from URL: {rca_url}")
                    return None
            else:
                self.logger.error(f"Could not extract page ID from URL: {rca_url}")
                return None
            
            # Get page content
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand='body.storage,version,space'
            )
            
            if not page:
                self.logger.error(f"Could not retrieve page content for ID: {page_id}")
                return None
            
            # Extract relevant information
            content_data = {
                'page_id': page_id,
                'title': page.get('title', ''),
                'content_html': page.get('body', {}).get('storage', {}).get('value', ''),
                'version': page.get('version', {}).get('number', 0),
                'space_key': page.get('space', {}).get('key', ''),
                'url': rca_url
            }
            
            self.logger.info(f"Successfully retrieved content for page: {content_data['title']}")
            return content_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving RCA content from {rca_url}: {str(e)}")
            return None
    
    def clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content to extract readable text for LLM analysis
        
        Args:
            html_content: Raw HTML content from Confluence
            
        Returns:
            Cleaned text content
        """
        try:
            from bs4 import BeautifulSoup
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except ImportError:
            self.logger.warning("BeautifulSoup not available, returning raw HTML")
            return html_content
        except Exception as e:
            self.logger.error(f"Error cleaning HTML content: {str(e)}")
            return html_content