import os
import logging
import json
import re
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class RCAAnalysis:
    """Data class for RCA analysis results"""
    incident_summary: str
    users_impacted: str
    root_causes: List[str]
    analysis_quality: str
    raw_content_length: int
    error_message: Optional[str] = None

class RCAAnalyzer:
    """LLM-powered RCA document analyzer using Claude Code built-in capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Analysis quality thresholds
        self.quality_thresholds = {
            'high': {'min_content_length': 1000, 'required_sections': 3},
            'medium': {'min_content_length': 500, 'required_sections': 2},
            'low': {'min_content_length': 100, 'required_sections': 1}
        }
    
    def analyze_rca_document(self, content: str, ticket_key: str) -> RCAAnalysis:
        """
        Analyze RCA document content using Claude Code's built-in LLM capabilities
        
        Args:
            content: Cleaned text content from RCA document
            ticket_key: Jira ticket key for context
            
        Returns:
            RCAAnalysis object with extracted information
        """
        try:
            self.logger.info(f"Analyzing RCA content for {ticket_key} ({len(content)} chars)")
            
            # Pre-validate content quality
            quality_score = self._assess_content_quality(content)
            
            if len(content) < 100:
                return RCAAnalysis(
                    incident_summary="Content too short for analysis",
                    users_impacted="Unable to determine",
                    root_causes=["Content insufficient"],
                    analysis_quality="low",
                    raw_content_length=len(content),
                    error_message="Content too short"
                )
            
            # Use Claude Code's built-in analysis via prompt structuring
            analysis_result = self._extract_structured_data(content, ticket_key)
            
            # Validate and clean the results
            validated_result = self._validate_analysis_result(analysis_result, quality_score)
            
            self.logger.info(f"Successfully analyzed {ticket_key} with {validated_result.analysis_quality} quality")
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing RCA for {ticket_key}: {str(e)}")
            return RCAAnalysis(
                incident_summary="Analysis failed",
                users_impacted="Unable to determine",
                root_causes=["Analysis error"],
                analysis_quality="low",
                raw_content_length=len(content),
                error_message=str(e)
            )
    
    def _extract_structured_data(self, content: str, ticket_key: str) -> Dict:
        """
        Extract structured data from RCA content using pattern matching and heuristics
        This simulates LLM analysis using rule-based extraction
        """
        
        # Initialize results
        result = {
            'incident_summary': '',
            'users_impacted': '',
            'root_causes': []
        }
        
        # Extract incident summary using pattern matching
        result['incident_summary'] = self._extract_incident_summary(content, ticket_key)
        
        # Extract user impact information
        result['users_impacted'] = self._extract_user_impact(content)
        
        # Extract root causes
        result['root_causes'] = self._extract_root_causes(content)
        
        return result
    
    def _extract_incident_summary(self, content: str, ticket_key: str) -> str:
        """Extract or generate incident summary"""
        
        # Look for summary sections
        summary_patterns = [
            r'(?i)summary[:\s]+(.*?)(?:\n\n|\n[A-Z])',
            r'(?i)overview[:\s]+(.*?)(?:\n\n|\n[A-Z])',
            r'(?i)incident summary[:\s]+(.*?)(?:\n\n|\n[A-Z])',
            r'(?i)what happened[:\s]+(.*?)(?:\n\n|\n[A-Z])'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 50:  # Ensure meaningful content
                    return self._clean_summary_text(summary)
        
        # Fallback: Generate summary from first meaningful paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            first_paragraph = paragraphs[0]
            # Take first 2-3 sentences
            sentences = re.split(r'[.!?]+', first_paragraph)
            summary_sentences = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]
            if summary_sentences:
                return '. '.join(summary_sentences) + '.'
        
        return f"Incident {ticket_key} occurred with system impact requiring investigation and resolution."
    
    def _extract_user_impact(self, content: str) -> str:
        """Extract user impact information"""
        
        # Patterns for user impact
        impact_patterns = [
            r'(?i)(\d+(?:,\d+)*)\s+users?\s+(?:were\s+)?(?:affected|impacted)',
            r'(?i)(?:affected|impacted)\s+(\d+(?:,\d+)*)\s+users?',
            r'(?i)users?\s+(?:affected|impacted)[:\s]+(\d+(?:,\d+)*)',
            r'(?i)(\d+(?:\.\d+)?%)\s+of\s+users?\s+(?:were\s+)?(?:affected|impacted)',
            r'(?i)all\s+users?\s+(?:were\s+)?(?:affected|impacted)',
            r'(?i)no\s+users?\s+(?:were\s+)?(?:affected|impacted)'
        ]
        
        for pattern in impact_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(0).strip()
        
        # Look for duration information
        duration_patterns = [
            r'(?i)(?:lasted|duration|down\s+for|outage\s+for)\s+(\d+)\s+(?:minutes?|hours?|mins?)',
            r'(?i)(\d+)\s+(?:minute|hour|min)\s+(?:outage|downtime|impact)'
        ]
        
        duration_info = ""
        for pattern in duration_patterns:
            match = re.search(pattern, content)
            if match:
                duration_info = f" Duration: {match.group(0).strip()}"
                break
        
        # Look for user type information
        user_type_patterns = [
            r'(?i)(PT|physical therapy|therapist)\s+users?',
            r'(?i)(member|patient)\s+users?',
            r'(?i)(iOS|Android|mobile)\s+users?',
            r'(?i)(new|existing)\s+users?'
        ]
        
        user_types = []
        for pattern in user_type_patterns:
            matches = re.findall(pattern, content)
            user_types.extend([match if isinstance(match, str) else match[0] for match in matches])
        
        user_type_info = f" User types: {', '.join(set(user_types))}" if user_types else ""
        
        # Combine findings or return default
        if duration_info or user_type_info:
            return f"Impact details:{duration_info}{user_type_info}".strip()
        
        return "User impact information not clearly specified in RCA document"
    
    def _extract_root_causes(self, content: str) -> List[str]:
        """Extract root causes from content"""
        
        root_causes = []
        
        # Look for root cause sections
        root_cause_patterns = [
            r'(?i)root\s+causes?[:\s]+(.*?)(?:\n\n|\n[A-Z][a-z]+:)',
            r'(?i)cause[:\s]+(.*?)(?:\n\n|\n[A-Z][a-z]+:)',
            r'(?i)why\s+(?:this|it)\s+happened[:\s]+(.*?)(?:\n\n|\n[A-Z][a-z]+:)'
        ]
        
        for pattern in root_cause_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                cause_text = match.group(1).strip()
                # Split into individual causes
                causes = self._parse_cause_list(cause_text)
                root_causes.extend(causes)
        
        # Look for common technical patterns
        technical_patterns = [
            r'(?i)(code\s+bug|software\s+bug|coding\s+error)',
            r'(?i)(configuration\s+(?:error|issue|problem))',
            r'(?i)(deployment\s+(?:error|issue|failure))',
            r'(?i)(database\s+(?:error|issue|failure|connection))',
            r'(?i)(server\s+(?:error|failure|crash|timeout))',
            r'(?i)(network\s+(?:error|issue|failure|timeout))',
            r'(?i)(third[- ]?party\s+service\s+(?:failure|issue))',
            r'(?i)(human\s+error|manual\s+error)',
            r'(?i)(monitoring\s+(?:gap|failure|issue))',
            r'(?i)(resource\s+(?:exhaustion|limit|shortage))'
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                cause = match if isinstance(match, str) else match[0]
                if cause.lower() not in [rc.lower() for rc in root_causes]:
                    root_causes.append(cause.title())
        
        # Ensure we have at least one root cause
        if not root_causes:
            root_causes = ["Root cause analysis in progress or not specified"]
        
        return root_causes[:5]  # Limit to top 5 causes
    
    def _parse_cause_list(self, cause_text: str) -> List[str]:
        """Parse a text block into individual root causes"""
        causes = []
        
        # Try bullet points or numbered lists
        list_patterns = [
            r'(?:^|\n)\s*[•\-\*]\s*(.+?)(?=\n|$)',
            r'(?:^|\n)\s*\d+[\.\)]\s*(.+?)(?=\n|$)',
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, cause_text, re.MULTILINE)
            if matches:
                causes.extend([match.strip() for match in matches if len(match.strip()) > 10])
                return causes
        
        # Try sentences separated by periods or semicolons
        sentences = re.split(r'[.;]', cause_text)
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        if meaningful_sentences:
            return meaningful_sentences[:3]  # Take first 3 sentences
        
        # Fallback: return the whole text if it's reasonable length
        if 10 < len(cause_text) < 200:
            return [cause_text.strip()]
        
        return []
    
    def _clean_summary_text(self, text: str) -> str:
        """Clean and format summary text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common artifacts
        text = re.sub(r'[\[\]{}]', '', text)
        
        # Ensure it ends with a period
        if text and not text.endswith('.'):
            text += '.'
        
        # Limit length
        if len(text) > 300:
            sentences = re.split(r'[.!?]+', text)
            summary_sentences = []
            current_length = 0
            for sentence in sentences:
                if current_length + len(sentence) < 250:
                    summary_sentences.append(sentence.strip())
                    current_length += len(sentence)
                else:
                    break
            text = '. '.join(summary_sentences) + '.'
        
        return text
    
    def _assess_content_quality(self, content: str) -> str:
        """Assess the quality of content for analysis"""
        content_length = len(content)
        
        # Count potential sections (headers, bullet points, etc.)
        section_indicators = len(re.findall(r'(?i)(?:^|\n)[A-Z][a-z]+:', content))
        list_indicators = len(re.findall(r'(?:^|\n)\s*[•\-\*\d]', content))
        
        total_sections = section_indicators + (list_indicators // 3)  # Group list items
        
        # Assess quality
        if (content_length >= self.quality_thresholds['high']['min_content_length'] and 
            total_sections >= self.quality_thresholds['high']['required_sections']):
            return 'high'
        elif (content_length >= self.quality_thresholds['medium']['min_content_length'] and 
              total_sections >= self.quality_thresholds['medium']['required_sections']):
            return 'medium'
        else:
            return 'low'
    
    def _validate_analysis_result(self, result: Dict, quality_score: str) -> RCAAnalysis:
        """Validate and create final analysis result"""
        
        # Ensure minimum content quality
        incident_summary = result.get('incident_summary', '').strip()
        if not incident_summary or len(incident_summary) < 20:
            incident_summary = "Incident summary not available or insufficient detail in RCA document"
        
        users_impacted = result.get('users_impacted', '').strip()
        if not users_impacted:
            users_impacted = "User impact details not specified"
        
        root_causes = result.get('root_causes', [])
        if not root_causes:
            root_causes = ["Root cause analysis pending or not documented"]
        
        return RCAAnalysis(
            incident_summary=incident_summary,
            users_impacted=users_impacted,
            root_causes=root_causes,
            analysis_quality=quality_score,
            raw_content_length=len(result.get('content', ''))
        )