#!/usr/bin/env python3
"""
Business Impact Analyzer for Incident Analysis

Analyzes RCA documents and incident data to extract business impact metrics
for engineering leadership visibility and decision-making.
"""

import re
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class BusinessImpactLevel(Enum):
    """Business impact severity levels"""
    CRITICAL = 10    # Revenue loss, major customer impact, regulatory
    HIGH = 8         # Significant user impact, SLA breach
    MEDIUM = 5       # Moderate user impact, degraded experience  
    LOW = 3          # Minor impact, limited scope
    MINIMAL = 1      # Negligible business impact

@dataclass
class BusinessImpactAnalysis:
    """Business impact analysis results"""
    impact_score: int                    # 1-10 scale
    customer_count_affected: str         # Quantified user impact
    revenue_impact_est: str              # Estimated revenue impact
    service_downtime_minutes: int        # Total downtime
    severity_justification: str          # Why this severity level
    
class BusinessImpactAnalyzer:
    """Analyzes incidents for business impact metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Revenue impact estimation keywords
        self.high_revenue_keywords = [
            'payment', 'billing', 'checkout', 'subscription', 'revenue',
            'transaction', 'purchase', 'order', 'financial'
        ]
        
        # Critical service keywords
        self.critical_service_keywords = [
            'login', 'authentication', 'auth', 'signup', 'registration',
            'core', 'main', 'primary', 'essential', 'critical'
        ]
        
        # Customer impact patterns
        self.customer_impact_patterns = [
            r'(\d+(?:,\d+)*)\s+(?:users?|members?|customers?)',      # "1,200 users"
            r'(\d+(?:\.\d+)?%)\s+of\s+(?:users?|members?)',          # "15% of users"
            r'(?:all|entire)\s+(?:user\s+)?base',                    # "all users"
            r'(\d+(?:,\d+)*)\s+(?:accounts?|profiles?)'              # "500 accounts"
        ]
    
    def analyze_business_impact(self, content: str, ticket_key: str, priority: str, 
                              summary: str, pods_engaged: str) -> BusinessImpactAnalysis:
        """
        Analyze business impact from RCA content and incident metadata
        
        Args:
            content: RCA document content
            ticket_key: Incident ticket key
            priority: P1, P2, P3, P4
            summary: Incident summary
            pods_engaged: Teams involved
            
        Returns:
            BusinessImpactAnalysis with quantified business impact
        """
        try:
            # Extract customer impact
            customer_count = self._extract_customer_impact(content, summary)
            
            # Calculate downtime
            downtime_minutes = self._extract_downtime(content)
            
            # Estimate revenue impact
            revenue_impact = self._estimate_revenue_impact(content, summary, priority, downtime_minutes)
            
            # Calculate business impact score
            impact_score = self._calculate_impact_score(priority, customer_count, downtime_minutes, 
                                                      content, summary, pods_engaged)
            
            # Generate severity justification
            justification = self._generate_severity_justification(impact_score, priority, 
                                                                customer_count, downtime_minutes)
            
            return BusinessImpactAnalysis(
                impact_score=impact_score,
                customer_count_affected=customer_count,
                revenue_impact_est=revenue_impact,
                service_downtime_minutes=downtime_minutes,
                severity_justification=justification
            )
            
        except Exception as e:
            self.logger.error(f"Business impact analysis failed for {ticket_key}: {str(e)}")
            return self._create_fallback_analysis(ticket_key, str(e))
    
    def _extract_customer_impact(self, content: str, summary: str) -> str:
        """Extract quantified customer impact"""
        combined_text = f"{content} {summary}".lower()
        
        # Look for specific numbers
        for pattern in self.customer_impact_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                if 'all' in match.group(0) or 'entire' in match.group(0):
                    return "All users affected"
                elif match.groups():
                    number = match.group(1)
                    if '%' in number:
                        return f"{number} of user base"
                    else:
                        return f"{number} users"
        
        # Look for qualitative descriptions
        if any(word in combined_text for word in ['all users', 'entire user base', 'everyone']):
            return "All users affected"
        elif any(word in combined_text for word in ['many users', 'multiple users', 'several']):
            return "Multiple users affected (unquantified)"
        elif any(word in combined_text for word in ['some users', 'few users', 'limited']):
            return "Limited users affected"
        else:
            return "User impact not specified"
    
    def _extract_downtime(self, content: str) -> int:
        """Extract service downtime in minutes"""
        
        # Patterns for different time formats
        time_patterns = [
            (r'(\d+)\s*hours?\s*(\d+)?\s*min', lambda h, m: int(h) * 60 + (int(m) if m else 0)),
            (r'(\d+(?:\.\d+)?)\s*hours?', lambda h: int(float(h) * 60)),
            (r'(\d+)\s*(?:mins?|minutes?)', lambda m: int(m)),
            (r'(\d+)\s*seconds?', lambda s: max(1, int(s) // 60))  # Convert seconds to minutes, min 1
        ]
        
        content_lower = content.lower()
        
        for pattern, converter in time_patterns:
            matches = re.finditer(pattern, content_lower)
            for match in matches:
                try:
                    if len(match.groups()) == 2:  # hours and minutes
                        return converter(match.group(1), match.group(2))
                    else:
                        return converter(match.group(1))
                except (ValueError, TypeError):
                    continue
        
        # Look for duration patterns
        duration_patterns = [
            r'lasted\s+(?:for\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'down\s+for\s+(\d+)\s*(?:mins?|minutes?)',
            r'outage\s+(?:of\s+)?(\d+)\s*(?:mins?|minutes?)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return 0  # No downtime found
    
    def _estimate_revenue_impact(self, content: str, summary: str, priority: str, downtime_minutes: int) -> str:
        """Estimate potential revenue impact"""
        combined_text = f"{content} {summary}".lower()
        
        # Check for revenue-critical services
        is_revenue_critical = any(keyword in combined_text for keyword in self.high_revenue_keywords)
        is_critical_service = any(keyword in combined_text for keyword in self.critical_service_keywords)
        
        # Rough revenue impact estimation based on priority and service type
        if priority == 'P1':
            if is_revenue_critical and downtime_minutes > 30:
                return "High: $50K+ potential revenue impact"
            elif is_critical_service and downtime_minutes > 15:
                return "Medium: $10K-50K potential impact"
            else:
                return "Medium: $5K-25K potential impact"
        elif priority == 'P2':
            if is_revenue_critical:
                return "Medium: $5K-25K potential impact"
            else:
                return "Low: $1K-10K potential impact"
        elif priority == 'P3':
            if is_revenue_critical:
                return "Low: $1K-5K potential impact"
            else:
                return "Minimal: <$1K potential impact"
        else:  # P4
            return "Minimal: <$500 potential impact"
    
    def _calculate_impact_score(self, priority: str, customer_count: str, downtime_minutes: int,
                               content: str, summary: str, pods_engaged: str) -> int:
        """Calculate business impact score (1-10)"""
        score = 1  # Base score
        
        # Priority weighting (40% of score)
        priority_scores = {'P1': 4, 'P2': 3, 'P3': 2, 'P4': 1}
        score += priority_scores.get(priority, 1)
        
        # Customer impact weighting (30% of score)
        if 'all users' in customer_count.lower():
            score += 3
        elif any(term in customer_count.lower() for term in ['%', 'thousand', 'k users']):
            score += 2
        elif 'multiple' in customer_count.lower() or 'several' in customer_count.lower():
            score += 1
        
        # Downtime weighting (20% of score)
        if downtime_minutes > 120:  # > 2 hours
            score += 2
        elif downtime_minutes > 30:  # > 30 minutes
            score += 1
        
        # Service criticality (10% of score)
        combined_text = f"{content} {summary}".lower()
        if any(keyword in combined_text for keyword in self.high_revenue_keywords):
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _generate_severity_justification(self, impact_score: int, priority: str, 
                                       customer_count: str, downtime_minutes: int) -> str:
        """Generate justification for severity level"""
        reasons = []
        
        if impact_score >= 8:
            reasons.append("Critical business impact")
        elif impact_score >= 6:
            reasons.append("Significant business impact")
        elif impact_score >= 4:
            reasons.append("Moderate business impact")
        else:
            reasons.append("Limited business impact")
        
        if priority in ['P1', 'P2']:
            reasons.append(f"{priority} incident with high urgency")
        
        if 'all users' in customer_count.lower():
            reasons.append("Complete service disruption")
        elif any(num in customer_count for num in ['%', 'thousand', 'k']):
            reasons.append("Large user base affected")
        
        if downtime_minutes > 60:
            reasons.append(f"Extended downtime ({downtime_minutes} minutes)")
        elif downtime_minutes > 0:
            reasons.append(f"Service interruption ({downtime_minutes} minutes)")
        
        return "; ".join(reasons)
    
    def _create_fallback_analysis(self, ticket_key: str, error_message: str) -> BusinessImpactAnalysis:
        """Create fallback analysis when processing fails"""
        return BusinessImpactAnalysis(
            impact_score=1,
            customer_count_affected="Analysis failed",
            revenue_impact_est="Unable to estimate",
            service_downtime_minutes=0,
            severity_justification=f"Business impact analysis failed: {error_message}"
        )