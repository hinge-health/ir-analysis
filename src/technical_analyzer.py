#!/usr/bin/env python3
"""
Technical Analyzer for Incident Analysis

Analyzes RCA documents for technical categorization, detection/resolution times,
and automation opportunities to support IC engineer analysis.
"""

import re
import logging
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum

class RootCauseCategory(Enum):
    """Technical root cause categories"""
    CODE_BUG = "Code Bug"
    CONFIGURATION = "Configuration Error"
    INFRASTRUCTURE = "Infrastructure Failure"
    DEPLOYMENT = "Deployment Issue"
    DEPENDENCY_FAILURE = "External Dependency"
    CAPACITY = "Capacity/Performance"
    PROCESS_FAILURE = "Process/Human Error"
    MONITORING_GAP = "Monitoring/Alerting Gap"
    UNKNOWN = "Unknown/Not Classified"

class TechnicalDebtLevel(Enum):
    """Technical debt impact levels"""
    HIGH = "High - Major refactoring needed"
    MEDIUM = "Medium - Some improvements required"
    LOW = "Low - Minor cleanup needed"
    NONE = "None - Well-architected solution"

@dataclass
class TechnicalAnalysis:
    """Technical analysis results"""
    root_cause_category: str        # Primary technical category
    detection_time_minutes: int     # Time to detect issue
    resolution_time_minutes: int    # Time to resolve issue
    technical_debt_level: str       # Technical debt assessment
    automation_score: int           # Automation opportunities (0-5)

class TechnicalAnalyzer:
    """Analyzes incidents for technical categorization and metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Root cause classification patterns
        self.cause_patterns = {
            RootCauseCategory.CODE_BUG: [
                'bug', 'error', 'exception', 'null pointer', 'index out of bounds',
                'race condition', 'memory leak', 'logic error', 'off by one'
            ],
            RootCauseCategory.CONFIGURATION: [
                'config', 'setting', 'parameter', 'environment variable', 'property',
                'misconfigured', 'wrong setting', 'configuration error'
            ],
            RootCauseCategory.INFRASTRUCTURE: [
                'server', 'hardware', 'network', 'database', 'disk space', 'memory',
                'cpu', 'load balancer', 'dns', 'ssl', 'certificate', 'aws', 'cloud'
            ],
            RootCauseCategory.DEPLOYMENT: [
                'deploy', 'release', 'rollback', 'version', 'build', 'pipeline',
                'ci/cd', 'migration', 'update', 'upgrade'
            ],
            RootCauseCategory.DEPENDENCY_FAILURE: [
                'third party', 'external', 'vendor', 'api', 'service', 'upstream',
                'downstream', 'integration', 'webhook', 'partner'
            ],
            RootCauseCategory.CAPACITY: [
                'capacity', 'performance', 'slow', 'timeout', 'overload', 'scaling',
                'traffic', 'load', 'bottleneck', 'latency', 'throughput'
            ],
            RootCauseCategory.PROCESS_FAILURE: [
                'human error', 'manual', 'process', 'procedure', 'forgot', 'missed',
                'training', 'communication', 'handoff'
            ],
            RootCauseCategory.MONITORING_GAP: [
                'monitoring', 'alert', 'detection', 'observability', 'logging',
                'metric', 'dashboard', 'notification', 'no alert'
            ]
        }
        
        # Automation opportunity indicators
        self.automation_indicators = {
            'runbook': 1,
            'manual process': 2,
            'human intervention': 2,
            'could be automated': 3,
            'should automate': 3,
            'repetitive': 2,
            'toil': 3,
            'script': 1,
            'automation': 1
        }
        
        # Technical debt indicators
        self.tech_debt_indicators = {
            'legacy': 2,
            'technical debt': 3,
            'refactor': 2,
            'architectural': 3,
            'workaround': 2,
            'hack': 3,
            'quick fix': 1,
            'temporary': 1,
            'cleanup': 1
        }
    
    def analyze_technical_aspects(self, content: str, ticket_key: str, 
                                 created_date: str) -> TechnicalAnalysis:
        """
        Analyze technical aspects of the incident
        
        Args:
            content: RCA document content
            ticket_key: Incident ticket key
            created_date: Incident creation timestamp
            
        Returns:
            TechnicalAnalysis with categorization and metrics
        """
        try:
            # Classify root cause category
            root_cause_category = self._classify_root_cause(content)
            
            # Extract timing metrics
            detection_time = self._extract_detection_time(content)
            resolution_time = self._extract_resolution_time(content)
            
            # Assess technical debt
            tech_debt_level = self._assess_technical_debt(content)
            
            # Calculate automation score
            automation_score = self._calculate_automation_score(content)
            
            return TechnicalAnalysis(
                root_cause_category=root_cause_category.value,
                detection_time_minutes=detection_time,
                resolution_time_minutes=resolution_time,
                technical_debt_level=tech_debt_level.value,
                automation_score=automation_score
            )
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed for {ticket_key}: {str(e)}")
            return self._create_fallback_analysis(ticket_key, str(e))
    
    def _classify_root_cause(self, content: str) -> RootCauseCategory:
        """Classify the root cause category based on content analysis"""
        content_lower = content.lower()
        category_scores = {}
        
        # Score each category based on keyword matches
        for category, keywords in self.cause_patterns.items():
            score = 0
            for keyword in keywords:
                # Count occurrences, but with diminishing returns
                occurrences = content_lower.count(keyword)
                if occurrences > 0:
                    score += min(occurrences, 3)  # Cap at 3 per keyword
            category_scores[category] = score
        
        # Find the highest scoring category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:  # At least one match
                return best_category[0]
        
        return RootCauseCategory.UNKNOWN
    
    def _extract_detection_time(self, content: str) -> int:
        """Extract time to detection in minutes"""
        
        # Patterns for detection time mentions
        detection_patterns = [
            r'detected?\s+(?:after\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'noticed?\s+(?:after\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'discovered?\s+(?:after\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'alert(?:ed)?\s+(?:after\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'time\s+to\s+detect(?:ion)?:?\s+(\d+)\s*(?:mins?|minutes?)',
            r'mttr?\s*[-:]?\s*(\d+)\s*(?:mins?|minutes?)'
        ]
        
        content_lower = content.lower()
        
        for pattern in detection_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # Look for hour-based patterns
        hour_patterns = [
            r'detected?\s+(?:after\s+)?(\d+(?:\.\d+)?)\s*hours?',
            r'time\s+to\s+detect(?:ion)?:?\s+(\d+(?:\.\d+)?)\s*hours?'
        ]
        
        for pattern in hour_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    hours = float(match.group(1))
                    return int(hours * 60)  # Convert to minutes
                except ValueError:
                    continue
        
        return 0  # No detection time found
    
    def _extract_resolution_time(self, content: str) -> int:
        """Extract time to resolution in minutes"""
        
        # Patterns for resolution time mentions
        resolution_patterns = [
            r'resolved?\s+(?:after\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'fixed?\s+(?:after\s+)?(\d+)\s*(?:mins?|minutes?)',
            r'time\s+to\s+fix:?\s+(\d+)\s*(?:mins?|minutes?)',
            r'time\s+to\s+resolv(?:e|ution):?\s+(\d+)\s*(?:mins?|minutes?)',
            r'took\s+(\d+)\s*(?:mins?|minutes?)\s+to\s+(?:fix|resolve)',
            r'resolution\s+time:?\s+(\d+)\s*(?:mins?|minutes?)'
        ]
        
        content_lower = content.lower()
        
        for pattern in resolution_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # Look for hour-based patterns
        hour_patterns = [
            r'resolved?\s+(?:after\s+)?(\d+(?:\.\d+)?)\s*hours?',
            r'took\s+(\d+(?:\.\d+)?)\s*hours?\s+to\s+(?:fix|resolve)',
            r'time\s+to\s+resolv(?:e|ution):?\s+(\d+(?:\.\d+)?)\s*hours?'
        ]
        
        for pattern in hour_patterns:
            match = re.search(pattern, content_lower)
            if match:
                try:
                    hours = float(match.group(1))
                    return int(hours * 60)  # Convert to minutes
                except ValueError:
                    continue
        
        return 0  # No resolution time found
    
    def _assess_technical_debt(self, content: str) -> TechnicalDebtLevel:
        """Assess technical debt level based on content"""
        content_lower = content.lower()
        debt_score = 0
        
        # Calculate debt score based on indicators
        for indicator, weight in self.tech_debt_indicators.items():
            occurrences = content_lower.count(indicator)
            debt_score += occurrences * weight
        
        # Check for architectural concerns
        architectural_terms = [
            'architecture', 'design flaw', 'structural', 'foundational',
            'system design', 'architectural debt'
        ]
        
        for term in architectural_terms:
            if term in content_lower:
                debt_score += 3
        
        # Classify debt level
        if debt_score >= 8:
            return TechnicalDebtLevel.HIGH
        elif debt_score >= 4:
            return TechnicalDebtLevel.MEDIUM
        elif debt_score >= 1:
            return TechnicalDebtLevel.LOW
        else:
            return TechnicalDebtLevel.NONE
    
    def _calculate_automation_score(self, content: str) -> int:
        """Calculate automation opportunity score (0-5)"""
        content_lower = content.lower()
        automation_score = 0
        
        # Base score from automation indicators
        for indicator, weight in self.automation_indicators.items():
            if indicator in content_lower:
                automation_score += weight
        
        # Additional scoring for specific scenarios
        if 'manual' in content_lower and 'process' in content_lower:
            automation_score += 2
        
        if 'human' in content_lower and ('error' in content_lower or 'intervention' in content_lower):
            automation_score += 2
        
        if any(term in content_lower for term in ['runbook', 'playbook', 'procedure']):
            automation_score += 1
        
        if any(term in content_lower for term in ['repetitive', 'recurring', 'pattern']):
            automation_score += 1
        
        # Look for prevention opportunities
        if 'prevent' in content_lower and 'automat' in content_lower:
            automation_score += 2
        
        return min(automation_score, 5)  # Cap at 5
    
    def _create_fallback_analysis(self, ticket_key: str, error_message: str) -> TechnicalAnalysis:
        """Create fallback analysis when processing fails"""
        return TechnicalAnalysis(
            root_cause_category=RootCauseCategory.UNKNOWN.value,
            detection_time_minutes=0,
            resolution_time_minutes=0,
            technical_debt_level=TechnicalDebtLevel.NONE.value,
            automation_score=0
        )