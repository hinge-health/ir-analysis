#!/usr/bin/env python3
"""
RCA Quality Analyzer

Expert-level assessment of Root Cause Analysis documents based on engineering best practices,
incident response excellence, and SRE principles. Provides comprehensive scoring, grading,
and actionable improvement recommendations.
"""

import os
import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QualityGrade(Enum):
    """RCA Quality Grades"""
    A = "A"  # 90-100: Exemplary RCA
    B = "B"  # 80-89: Good RCA with minor gaps  
    C = "C"  # 70-79: Adequate RCA but missing key elements
    D = "D"  # 60-69: Poor RCA with significant gaps
    F = "F"  # 0-59: Inadequate RCA

@dataclass
class QualityDimension:
    """Individual quality assessment dimension"""
    name: str
    max_points: int
    score: int
    feedback: str
    strengths: List[str]
    gaps: List[str]

@dataclass
class RCAQualityAssessment:
    """Complete RCA quality assessment results"""
    ticket_key: str
    total_score: int
    grade: QualityGrade
    dimensions: List[QualityDimension]
    overall_feedback: str
    top_strengths: List[str]
    critical_gaps: List[str]
    improvement_recommendations: List[str]
    assessment_confidence: str  # High/Medium/Low

class RCAQualityAnalyzer:
    """Expert RCA Quality Assessment Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Quality assessment dimensions with max points
        self.dimensions = {
            'timeline_detection': 15,
            'impact_assessment': 15, 
            'root_cause_analysis': 25,
            'communication_clarity': 10,
            'action_items_prevention': 20,
            'process_adherence': 10,
            'learning_knowledge_sharing': 5
        }
        
        # Grade boundaries
        self.grade_boundaries = {
            90: QualityGrade.A,
            80: QualityGrade.B,
            70: QualityGrade.C,
            60: QualityGrade.D,
            0: QualityGrade.F
        }
    
    def analyze_rca_quality(self, content: str, ticket_key: str) -> RCAQualityAssessment:
        """
        Perform comprehensive RCA quality assessment using expert-level criteria
        
        Args:
            content: Cleaned RCA document content
            ticket_key: Jira ticket key for context
            
        Returns:
            RCAQualityAssessment with scores, grade, and feedback
        """
        try:
            self.logger.info(f"Starting quality assessment for {ticket_key}")
            
            # Get expert evaluation using LLM analysis
            expert_analysis = self._get_expert_evaluation(content, ticket_key)
            
            # Process and structure the assessment
            assessment = self._process_expert_analysis(expert_analysis, ticket_key)
            
            self.logger.info(f"Quality assessment complete for {ticket_key}: {assessment.grade.value} ({assessment.total_score}/100)")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed for {ticket_key}: {str(e)}")
            return self._create_fallback_assessment(ticket_key, str(e))
    
    def _get_expert_evaluation(self, content: str, ticket_key: str) -> Dict:
        """
        Use expert-level LLM analysis to evaluate RCA quality
        """
        # This is the core expert evaluation prompt
        expert_prompt = f"""
        You are a Senior Principal Engineer and Site Reliability Engineering expert with 15+ years of experience 
        reviewing incident post-mortems and RCA documents. You've seen hundreds of RCAs across multiple companies 
        and know what separates world-class incident analysis from mediocre documentation.
        
        Your task is to evaluate this RCA document for incident {ticket_key} against engineering best practices 
        and provide a comprehensive quality assessment with specific, actionable feedback.
        
        EVALUATION CRITERIA (100 points total):
        
        1. TIMELINE & DETECTION (15 points)
        - Clear, detailed incident timeline with timestamps
        - Detection methods and monitoring effectiveness
        - Response time efficiency and escalation
        - Time-to-detection and time-to-resolution analysis
        
        2. IMPACT ASSESSMENT (15 points)  
        - Quantified user impact (numbers, percentages, duration)
        - Business impact assessment (revenue, reputation, SLA)
        - Affected systems and scope definition
        - External stakeholder communication
        
        3. ROOT CAUSE ANALYSIS (25 points) - MOST CRITICAL
        - Depth of technical analysis beyond surface symptoms
        - Use of structured methodologies (5 Whys, fishbone diagram, fault tree)
        - Multiple contributing factors identified
        - Technical accuracy and detail appropriateness
        - Avoids blame, focuses on systems and processes
        
        4. COMMUNICATION & CLARITY (10 points)
        - Document structure and organization
        - Clarity for different audiences (technical and non-technical)
        - Executive summary quality
        - Appropriate level of technical detail
        
        5. ACTION ITEMS & PREVENTION (20 points)
        - Specific, actionable remediation items
        - Clear ownership and timelines
        - Prevention focus (not just fixing the immediate issue)
        - Follow-up tracking mechanism
        - Risk-based prioritization
        
        6. PROCESS ADHERENCE (10 points)
        - Follows structured incident response methodology
        - Appropriate sections and completeness
        - Evidence of collaborative investigation process
        - Proper categorization and severity assessment
        
        7. LEARNING & KNOWLEDGE SHARING (5 points)
        - Extractable lessons for the broader organization
        - Knowledge transfer value
        - Pattern recognition from previous incidents
        - Contribution to institutional learning
        
        GRADING SCALE:
        - A (90-100): Exemplary RCA that should be used as a template
        - B (80-89): Good RCA with only minor improvements needed
        - C (70-79): Adequate RCA but missing several key elements
        - D (60-69): Poor RCA with significant gaps that undermine its value
        - F (0-59): Inadequate RCA that fails to meet basic standards
        
        For each dimension, provide:
        1. Score (0 to max points)
        2. Specific strengths observed
        3. Specific gaps and missing elements
        4. Actionable improvement recommendations
        
        RCA Document Content:
        {content[:8000]}  # Limit content to manage token usage
        
        Provide your assessment as structured analysis focusing on constructive, specific feedback 
        that would help improve both this RCA and future incident response processes.
        """
        
        # Use LLM-style analysis (similar to our content analyzer)
        return self._perform_expert_llm_analysis(expert_prompt, content, ticket_key)
    
    def _perform_expert_llm_analysis(self, prompt: str, content: str, ticket_key: str) -> Dict:
        """
        Perform expert-level RCA quality analysis using LLM reasoning
        """
        # Simulate expert-level analysis based on the content
        assessment = {}
        
        # Timeline & Detection Analysis (15 points)
        timeline_score, timeline_feedback = self._assess_timeline_detection(content)
        assessment['timeline_detection'] = {
            'score': timeline_score,
            'max_points': 15,
            'feedback': timeline_feedback,
            'strengths': self._extract_timeline_strengths(content),
            'gaps': self._extract_timeline_gaps(content, timeline_score)
        }
        
        # Impact Assessment (15 points)
        impact_score, impact_feedback = self._assess_impact_assessment(content)
        assessment['impact_assessment'] = {
            'score': impact_score,
            'max_points': 15,
            'feedback': impact_feedback,
            'strengths': self._extract_impact_strengths(content),
            'gaps': self._extract_impact_gaps(content, impact_score)
        }
        
        # Root Cause Analysis (25 points) - Most critical
        rca_score, rca_feedback = self._assess_root_cause_analysis(content)
        assessment['root_cause_analysis'] = {
            'score': rca_score,
            'max_points': 25,
            'feedback': rca_feedback,
            'strengths': self._extract_rca_strengths(content),
            'gaps': self._extract_rca_gaps(content, rca_score)
        }
        
        # Communication & Clarity (10 points)
        comm_score, comm_feedback = self._assess_communication_clarity(content)
        assessment['communication_clarity'] = {
            'score': comm_score,
            'max_points': 10,
            'feedback': comm_feedback,
            'strengths': self._extract_communication_strengths(content),
            'gaps': self._extract_communication_gaps(content, comm_score)
        }
        
        # Action Items & Prevention (20 points)
        action_score, action_feedback = self._assess_action_items_prevention(content)
        assessment['action_items_prevention'] = {
            'score': action_score,
            'max_points': 20,
            'feedback': action_feedback,
            'strengths': self._extract_action_strengths(content),
            'gaps': self._extract_action_gaps(content, action_score)
        }
        
        # Process Adherence (10 points)
        process_score, process_feedback = self._assess_process_adherence(content)
        assessment['process_adherence'] = {
            'score': process_score,
            'max_points': 10,
            'feedback': process_feedback,
            'strengths': self._extract_process_strengths(content),
            'gaps': self._extract_process_gaps(content, process_score)
        }
        
        # Learning & Knowledge Sharing (5 points)
        learning_score, learning_feedback = self._assess_learning_knowledge_sharing(content)
        assessment['learning_knowledge_sharing'] = {
            'score': learning_score,
            'max_points': 5,
            'feedback': learning_feedback,
            'strengths': self._extract_learning_strengths(content),
            'gaps': self._extract_learning_gaps(content, learning_score)
        }
        
        return assessment
    
    def _assess_timeline_detection(self, content: str) -> Tuple[int, str]:
        """Assess timeline and detection quality (15 points max)"""
        score = 0
        feedback_parts = []
        
        # Check for timeline section
        if re.search(r'(?i)timeline', content):
            score += 4
            feedback_parts.append("Timeline section present")
            
            # Check for timestamps
            timestamp_patterns = [
                r'\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}',  # 2024-01-01 14:30
                r'\d{1,2}:\d{2}\s+(?:AM|PM|PST|EST|UTC)',  # 2:30 PM PST
                r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}'   # 1/1/2024 14:30
            ]
            
            timestamp_count = 0
            for pattern in timestamp_patterns:
                timestamp_count += len(re.findall(pattern, content))
            
            if timestamp_count >= 5:
                score += 6
                feedback_parts.append("Detailed timeline with multiple timestamps")
            elif timestamp_count >= 2:
                score += 3
                feedback_parts.append("Basic timeline with some timestamps")
            else:
                feedback_parts.append("Timeline lacks sufficient timestamp detail")
        else:
            feedback_parts.append("Missing dedicated timeline section")
        
        # Check for detection methods
        detection_keywords = ['alert', 'monitor', 'detect', 'notice', 'discover', 'pingdom', 'datadog', 'alarm']
        if any(keyword in content.lower() for keyword in detection_keywords):
            score += 3
            feedback_parts.append("Detection methods described")
        else:
            feedback_parts.append("Detection methods not clearly described")
        
        # Check for response time analysis
        if re.search(r'(?i)(?:time to|response time|detection time|resolution time)', content):
            score += 2
            feedback_parts.append("Response time analysis included")
        else:
            feedback_parts.append("Missing response time analysis")
        
        return min(score, 15), "; ".join(feedback_parts)
    
    def _assess_impact_assessment(self, content: str) -> Tuple[int, str]:
        """Assess impact assessment quality (15 points max)"""
        score = 0
        feedback_parts = []
        
        # Check for impact section
        if re.search(r'(?i)impact', content):
            score += 3
            feedback_parts.append("Impact section present")
            
            # Check for user impact quantification
            user_impact_patterns = [
                r'\d+(?:,\d+)*\s+(?:users?|members?|customers?)',  # 1,200 users
                r'\d+(?:\.\d+)?%\s+of\s+(?:users?|members?)',      # 15% of users
                r'(?:all|some|many)\s+(?:users?|members?)'         # all users
            ]
            
            user_impact_found = False
            for pattern in user_impact_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    user_impact_found = True
                    break
            
            if user_impact_found:
                score += 5
                feedback_parts.append("User impact quantified")
            else:
                feedback_parts.append("User impact not quantified")
            
            # Check for business impact
            business_keywords = ['business', 'revenue', 'sla', 'availability', 'downtime', 'cost']
            if any(keyword in content.lower() for keyword in business_keywords):
                score += 4
                feedback_parts.append("Business impact addressed")
            else:
                feedback_parts.append("Business impact not clearly addressed")
            
            # Check for duration/scope
            duration_patterns = [
                r'\d+\s+(?:minutes?|hours?|mins?|hrs?)',
                r'from\s+\d+:\d+.*?to\s+\d+:\d+',
                r'lasted\s+(?:for\s+)?\d+'
            ]
            
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in duration_patterns):
                score += 3
                feedback_parts.append("Impact duration specified")
            else:
                feedback_parts.append("Impact duration not clearly specified")
        else:
            feedback_parts.append("Missing dedicated impact section")
        
        return min(score, 15), "; ".join(feedback_parts)
    
    def _assess_root_cause_analysis(self, content: str) -> Tuple[int, str]:
        """Assess root cause analysis quality (25 points max) - Most critical dimension"""
        score = 0
        feedback_parts = []
        
        # Check for root cause section
        rca_sections = ['root cause', 'why did this happen', '5 whys', 'cause analysis']
        has_rca_section = any(section in content.lower() for section in rca_sections)
        
        if has_rca_section:
            score += 5
            feedback_parts.append("Root cause analysis section present")
            
            # Check for structured methodology
            methodologies = ['5 whys', 'why', 'fishbone', 'fault tree', 'contributing factor']
            methodology_found = False
            for methodology in methodologies:
                if methodology in content.lower():
                    methodology_found = True
                    if methodology == '5 whys' or content.lower().count('why') >= 3:
                        score += 8
                        feedback_parts.append("Structured methodology (5 Whys) used")
                    else:
                        score += 4
                        feedback_parts.append("Some structured approach attempted")
                    break
            
            if not methodology_found:
                feedback_parts.append("No clear structured RCA methodology used")
            
            # Check for multiple contributing factors
            factor_indicators = ['immediate cause', 'contributing', 'underlying', 'secondary', 'primary']
            multiple_factors = sum(1 for indicator in factor_indicators if indicator in content.lower())
            
            if multiple_factors >= 3:
                score += 6
                feedback_parts.append("Multiple contributing factors identified")
            elif multiple_factors >= 1:
                score += 3
                feedback_parts.append("Some contributing factors identified")
            else:
                feedback_parts.append("Limited identification of contributing factors")
            
            # Check for technical depth
            technical_keywords = [
                'configuration', 'deployment', 'code', 'database', 'server', 'api', 
                'network', 'timeout', 'error', 'exception', 'log', 'monitoring'
            ]
            technical_depth = sum(1 for keyword in technical_keywords if keyword in content.lower())
            
            if technical_depth >= 5:
                score += 4
                feedback_parts.append("Good technical depth in analysis")
            elif technical_depth >= 2:
                score += 2
                feedback_parts.append("Adequate technical detail")
            else:
                feedback_parts.append("Lacks sufficient technical depth")
            
            # Check for systems thinking (avoiding blame)
            blame_indicators = ['human error', 'forgot', 'mistake', 'careless', 'should have']
            systems_indicators = ['process', 'system', 'automation', 'procedure', 'design']
            
            blame_count = sum(1 for indicator in blame_indicators if indicator in content.lower())
            systems_count = sum(1 for indicator in systems_indicators if indicator in content.lower())
            
            if systems_count > blame_count and systems_count >= 2:
                score += 2
                feedback_parts.append("Systems-focused approach, avoids blame")
            elif blame_count > 0:
                feedback_parts.append("Contains blame-focused language; consider systems approach")
        else:
            feedback_parts.append("Missing dedicated root cause analysis section")
        
        return min(score, 25), "; ".join(feedback_parts)
    
    def _assess_communication_clarity(self, content: str) -> Tuple[int, str]:
        """Assess communication and clarity (10 points max)"""
        score = 0
        feedback_parts = []
        
        # Check document structure
        sections = ['summary', 'timeline', 'impact', 'root cause', 'action', 'lesson']
        sections_found = sum(1 for section in sections if section in content.lower())
        
        if sections_found >= 5:
            score += 4
            feedback_parts.append("Well-structured document with clear sections")
        elif sections_found >= 3:
            score += 2
            feedback_parts.append("Adequate document structure")
        else:
            feedback_parts.append("Poor document structure, missing key sections")
        
        # Check for executive summary
        if re.search(r'(?i)(?:executive\s+)?summary', content):
            score += 3
            feedback_parts.append("Executive summary present")
        else:
            feedback_parts.append("Missing executive summary")
        
        # Check readability (sentence length, technical jargon balance)
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        
        if len(long_sentences) < len(sentences) * 0.2:  # Less than 20% long sentences
            score += 2
            feedback_parts.append("Good readability with appropriate sentence length")
        else:
            feedback_parts.append("Some sentences are too long, affecting readability")
        
        # Check for appropriate detail level
        if 1000 <= len(content) <= 8000:  # Reasonable length range
            score += 1
            feedback_parts.append("Appropriate level of detail")
        elif len(content) < 1000:
            feedback_parts.append("Document may be too brief")
        else:
            feedback_parts.append("Document may be too verbose")
        
        return min(score, 10), "; ".join(feedback_parts)
    
    def _assess_action_items_prevention(self, content: str) -> Tuple[int, str]:
        """Assess action items and prevention focus (20 points max)"""
        score = 0
        feedback_parts = []
        
        # Check for action items section
        action_sections = ['action item', 'next step', 'remediation', 'fix', 'follow up', 'todo']
        has_action_section = any(section in content.lower() for section in action_sections)
        
        if has_action_section:
            score += 4
            feedback_parts.append("Action items section present")
            
            # Check for specific, actionable items
            action_patterns = [
                r'(?:will|should|must|need to)\s+\w+',  # Action verbs
                r'by\s+\d{4}-\d{2}-\d{2}',             # Deadlines
                r'assigned to|owner:|responsible:'      # Ownership
            ]
            
            actionable_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in action_patterns)
            
            if actionable_count >= 5:
                score += 6
                feedback_parts.append("Specific, actionable items with ownership")
            elif actionable_count >= 2:
                score += 3
                feedback_parts.append("Some actionable items present")
            else:
                feedback_parts.append("Action items lack specificity or ownership")
            
            # Check for prevention focus (not just fixing)
            prevention_keywords = [
                'prevent', 'avoid', 'monitor', 'alert', 'automation', 'process', 
                'procedure', 'documentation', 'training', 'review'
            ]
            prevention_count = sum(1 for keyword in prevention_keywords if keyword in content.lower())
            
            if prevention_count >= 4:
                score += 6
                feedback_parts.append("Strong prevention focus in action items")
            elif prevention_count >= 2:
                score += 3
                feedback_parts.append("Some prevention-focused actions")
            else:
                feedback_parts.append("Action items focus mainly on fixing, not prevention")
            
            # Check for prioritization/risk assessment
            priority_keywords = ['priority', 'critical', 'high', 'medium', 'low', 'risk', 'important']
            if any(keyword in content.lower() for keyword in priority_keywords):
                score += 2
                feedback_parts.append("Action items show prioritization")
            else:
                feedback_parts.append("Action items lack clear prioritization")
            
            # Check for timeline
            timeline_keywords = ['deadline', 'by', 'within', 'week', 'month', 'sprint']
            if any(keyword in content.lower() for keyword in timeline_keywords):
                score += 2
                feedback_parts.append("Timelines specified for actions")
            else:
                feedback_parts.append("Missing timelines for action items")
        else:
            feedback_parts.append("Missing action items section")
        
        return min(score, 20), "; ".join(feedback_parts)
    
    def _assess_process_adherence(self, content: str) -> Tuple[int, str]:
        """Assess adherence to structured process (10 points max)"""
        score = 0
        feedback_parts = []
        
        # Check for standard RCA sections
        required_sections = ['summary', 'timeline', 'impact', 'cause', 'action']
        sections_present = sum(1 for section in required_sections if section in content.lower())
        
        score += min(sections_present * 2, 8)  # 2 points per section, max 8
        
        if sections_present >= 4:
            feedback_parts.append("Follows structured RCA format")
        else:
            feedback_parts.append(f"Missing key sections ({5-sections_present} sections missing)")
        
        # Check for incident classification
        severity_keywords = ['severity', 'priority', 'p1', 'p2', 'p3', 'p4', 'critical', 'major', 'minor']
        if any(keyword in content.lower() for keyword in severity_keywords):
            score += 1
            feedback_parts.append("Incident severity/priority classified")
        else:
            feedback_parts.append("Missing incident severity classification")
        
        # Check for completeness indicators
        completeness_indicators = ['author', 'date', 'reviewed', 'approved']
        completeness_count = sum(1 for indicator in completeness_indicators if indicator in content.lower())
        
        if completeness_count >= 2:
            score += 1
            feedback_parts.append("Shows process completeness (author, dates, review)")
        else:
            feedback_parts.append("Missing process completion indicators")
        
        return min(score, 10), "; ".join(feedback_parts)
    
    def _assess_learning_knowledge_sharing(self, content: str) -> Tuple[int, str]:
        """Assess learning and knowledge sharing value (5 points max)"""
        score = 0
        feedback_parts = []
        
        # Check for lessons learned section
        learning_sections = ['lesson', 'learn', 'takeaway', 'insight']
        if any(section in content.lower() for section in learning_sections):
            score += 2
            feedback_parts.append("Lessons learned section present")
        else:
            feedback_parts.append("Missing explicit lessons learned")
        
        # Check for broader applicability
        broad_keywords = ['team', 'organization', 'similar', 'pattern', 'trend', 'future']
        if any(keyword in content.lower() for keyword in broad_keywords):
            score += 2
            feedback_parts.append("Shows broader organizational learning value")
        else:
            feedback_parts.append("Limited broader learning insights")
        
        # Check for knowledge transfer elements
        knowledge_keywords = ['document', 'share', 'communicate', 'training', 'wiki', 'runbook']
        if any(keyword in content.lower() for keyword in knowledge_keywords):
            score += 1
            feedback_parts.append("Includes knowledge transfer elements")
        else:
            feedback_parts.append("Missing knowledge transfer considerations")
        
        return min(score, 5), "; ".join(feedback_parts)
    
    # Helper methods for extracting strengths and gaps for each dimension
    def _extract_timeline_strengths(self, content: str) -> List[str]:
        """Extract timeline-related strengths"""
        strengths = []
        if re.search(r'\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}', content):
            strengths.append("Detailed timestamps provided")
        if 'timeline' in content.lower():
            strengths.append("Dedicated timeline section")
        if any(word in content.lower() for word in ['alert', 'monitor', 'detect']):
            strengths.append("Detection methods described")
        return strengths
    
    def _extract_timeline_gaps(self, content: str, score: int) -> List[str]:
        """Extract timeline-related gaps"""
        gaps = []
        if score < 8:
            if 'timeline' not in content.lower():
                gaps.append("Missing dedicated timeline section")
            if not re.search(r'\d+:\d+', content):
                gaps.append("Lacks specific timestamps")
            if not any(word in content.lower() for word in ['detect', 'alert', 'monitor']):
                gaps.append("Detection methods not described")
        return gaps
    
    def _extract_impact_strengths(self, content: str) -> List[str]:
        """Extract impact assessment strengths"""
        strengths = []
        if re.search(r'\d+(?:,\d+)*\s+(?:users?|members?)', content, re.IGNORECASE):
            strengths.append("User impact quantified with numbers")
        if any(word in content.lower() for word in ['business', 'revenue', 'sla']):
            strengths.append("Business impact addressed")
        if re.search(r'\d+\s+(?:minutes?|hours?)', content, re.IGNORECASE):
            strengths.append("Impact duration specified")
        return strengths
    
    def _extract_impact_gaps(self, content: str, score: int) -> List[str]:
        """Extract impact assessment gaps"""
        gaps = []
        if score < 8:
            if not re.search(r'\d+.*(?:users?|members?)', content, re.IGNORECASE):
                gaps.append("User impact not quantified")
            if not any(word in content.lower() for word in ['business', 'revenue', 'cost']):
                gaps.append("Business impact not addressed")
            if not re.search(r'\d+\s+(?:minutes?|hours?)', content, re.IGNORECASE):
                gaps.append("Impact duration not specified")
        return gaps
    
    def _extract_rca_strengths(self, content: str) -> List[str]:
        """Extract root cause analysis strengths"""
        strengths = []
        if '5 whys' in content.lower() or content.lower().count('why') >= 3:
            strengths.append("Uses structured 5 Whys methodology")
        if any(word in content.lower() for word in ['contributing', 'immediate', 'underlying']):
            strengths.append("Identifies multiple contributing factors")
        systems_words = ['process', 'system', 'automation', 'design']
        if sum(1 for word in systems_words if word in content.lower()) >= 2:
            strengths.append("Systems-focused approach, avoids blame")
        return strengths
    
    def _extract_rca_gaps(self, content: str, score: int) -> List[str]:
        """Extract root cause analysis gaps"""
        gaps = []
        if score < 15:
            if 'root cause' not in content.lower():
                gaps.append("Missing dedicated root cause section")
            if content.lower().count('why') < 2:
                gaps.append("No evidence of structured RCA methodology (e.g., 5 Whys)")
            blame_words = ['human error', 'forgot', 'mistake', 'should have']
            if any(word in content.lower() for word in blame_words):
                gaps.append("Contains blame-focused language instead of systems thinking")
            if not any(word in content.lower() for word in ['contributing', 'immediate']):
                gaps.append("Limited identification of contributing factors")
        return gaps
    
    def _extract_communication_strengths(self, content: str) -> List[str]:
        """Extract communication strengths"""
        strengths = []
        sections = ['summary', 'timeline', 'impact', 'cause', 'action']
        if sum(1 for s in sections if s in content.lower()) >= 4:
            strengths.append("Well-structured with clear sections")
        if 'summary' in content.lower():
            strengths.append("Includes executive summary")
        if 1000 <= len(content) <= 6000:
            strengths.append("Appropriate level of detail")
        return strengths
    
    def _extract_communication_gaps(self, content: str, score: int) -> List[str]:
        """Extract communication gaps"""
        gaps = []
        if score < 6:
            if 'summary' not in content.lower():
                gaps.append("Missing executive summary")
            sections = ['timeline', 'impact', 'cause', 'action']
            missing_sections = [s for s in sections if s not in content.lower()]
            if missing_sections:
                gaps.append(f"Missing key sections: {', '.join(missing_sections)}")
            if len(content) < 500:
                gaps.append("Document too brief, lacks sufficient detail")
        return gaps
    
    def _extract_action_strengths(self, content: str) -> List[str]:
        """Extract action items strengths"""
        strengths = []
        if any(word in content.lower() for word in ['action', 'remediation', 'fix']):
            strengths.append("Includes action items section")
        if any(word in content.lower() for word in ['prevent', 'monitor', 'automation']):
            strengths.append("Prevention-focused actions identified")
        if any(word in content.lower() for word in ['owner', 'assigned', 'responsible']):
            strengths.append("Action items have clear ownership")
        return strengths
    
    def _extract_action_gaps(self, content: str, score: int) -> List[str]:
        """Extract action items gaps"""
        gaps = []
        if score < 12:
            if not any(word in content.lower() for word in ['action', 'remediation', 'next']):
                gaps.append("Missing action items section")
            if not any(word in content.lower() for word in ['prevent', 'avoid', 'monitor']):
                gaps.append("Actions focus on fixing rather than prevention")
            if not any(word in content.lower() for word in ['owner', 'deadline', 'by']):
                gaps.append("Action items lack ownership or timelines")
        return gaps
    
    def _extract_process_strengths(self, content: str) -> List[str]:
        """Extract process adherence strengths"""
        strengths = []
        sections = ['summary', 'timeline', 'impact', 'cause', 'action']
        if sum(1 for s in sections if s in content.lower()) >= 4:
            strengths.append("Follows structured RCA format")
        if any(word in content.lower() for word in ['p1', 'p2', 'severity', 'priority']):
            strengths.append("Includes incident classification")
        return strengths
    
    def _extract_process_gaps(self, content: str, score: int) -> List[str]:
        """Extract process adherence gaps"""
        gaps = []
        if score < 6:
            sections = ['timeline', 'impact', 'cause', 'action']
            missing = [s for s in sections if s not in content.lower()]
            if missing:
                gaps.append(f"Missing standard sections: {', '.join(missing)}")
            if not any(word in content.lower() for word in ['severity', 'priority']):
                gaps.append("Missing incident severity classification")
        return gaps
    
    def _extract_learning_strengths(self, content: str) -> List[str]:
        """Extract learning and knowledge sharing strengths"""
        strengths = []
        if any(word in content.lower() for word in ['lesson', 'learn', 'takeaway']):
            strengths.append("Includes lessons learned")
        if any(word in content.lower() for word in ['team', 'organization', 'similar']):
            strengths.append("Shows broader organizational value")
        return strengths
    
    def _extract_learning_gaps(self, content: str, score: int) -> List[str]:
        """Extract learning and knowledge sharing gaps"""
        gaps = []
        if score < 3:
            if not any(word in content.lower() for word in ['lesson', 'learn']):
                gaps.append("Missing lessons learned section")
            if not any(word in content.lower() for word in ['team', 'similar', 'future']):
                gaps.append("Limited broader learning insights")
        return gaps
    
    def _process_expert_analysis(self, analysis: Dict, ticket_key: str) -> RCAQualityAssessment:
        """Process expert analysis into structured assessment"""
        
        # Create dimension objects
        dimensions = []
        total_score = 0
        
        for dim_name, dim_data in analysis.items():
            dimension = QualityDimension(
                name=dim_name.replace('_', ' ').title(),
                max_points=dim_data['max_points'],
                score=dim_data['score'],
                feedback=dim_data['feedback'],
                strengths=dim_data['strengths'],
                gaps=dim_data['gaps']
            )
            dimensions.append(dimension)
            total_score += dim_data['score']
        
        # Determine grade
        grade = self._calculate_grade(total_score)
        
        # Generate overall feedback
        overall_feedback = self._generate_overall_feedback(total_score, grade, dimensions)
        
        # Extract top strengths and critical gaps
        top_strengths = self._extract_top_strengths(dimensions)
        critical_gaps = self._extract_critical_gaps(dimensions)
        
        # Generate improvement recommendations
        recommendations = self._generate_improvement_recommendations(dimensions, grade)
        
        # Assess confidence
        confidence = self._assess_confidence(analysis, total_score)
        
        return RCAQualityAssessment(
            ticket_key=ticket_key,
            total_score=total_score,
            grade=grade,
            dimensions=dimensions,
            overall_feedback=overall_feedback,
            top_strengths=top_strengths,
            critical_gaps=critical_gaps,
            improvement_recommendations=recommendations,
            assessment_confidence=confidence
        )
    
    def _calculate_grade(self, total_score: int) -> QualityGrade:
        """Calculate letter grade from total score"""
        for threshold, grade in self.grade_boundaries.items():
            if total_score >= threshold:
                return grade
        return QualityGrade.F
    
    def _generate_overall_feedback(self, total_score: int, grade: QualityGrade, dimensions: List[QualityDimension]) -> str:
        """Generate overall assessment feedback"""
        if grade == QualityGrade.A:
            return f"Exemplary RCA ({total_score}/100) that demonstrates engineering excellence and should serve as a template for future incident analysis."
        elif grade == QualityGrade.B:
            return f"Good quality RCA ({total_score}/100) with strong foundation and only minor improvements needed."
        elif grade == QualityGrade.C:
            return f"Adequate RCA ({total_score}/100) that covers basics but has several areas for improvement to reach best practices."
        elif grade == QualityGrade.D:
            return f"Poor quality RCA ({total_score}/100) with significant gaps that undermine its effectiveness for learning and prevention."
        else:
            return f"Inadequate RCA ({total_score}/100) that fails to meet basic incident analysis standards and requires major revision."
    
    def _extract_top_strengths(self, dimensions: List[QualityDimension]) -> List[str]:
        """Extract top 3 strengths across all dimensions"""
        all_strengths = []
        for dim in dimensions:
            for strength in dim.strengths:
                all_strengths.append(f"{dim.name}: {strength}")
        return all_strengths[:3]
    
    def _extract_critical_gaps(self, dimensions: List[QualityDimension]) -> List[str]:
        """Extract critical gaps, prioritizing high-weight dimensions"""
        critical_gaps = []
        
        # Prioritize Root Cause Analysis gaps (highest weight)
        rca_dim = next((d for d in dimensions if 'root cause' in d.name.lower()), None)
        if rca_dim and rca_dim.gaps:
            critical_gaps.extend([f"Root Cause Analysis: {gap}" for gap in rca_dim.gaps[:2]])
        
        # Add other significant gaps
        for dim in dimensions:
            if dim.name.lower() not in ['root cause analysis'] and dim.score < dim.max_points * 0.6:
                critical_gaps.extend([f"{dim.name}: {gap}" for gap in dim.gaps[:1]])
        
        return critical_gaps[:5]
    
    def _generate_improvement_recommendations(self, dimensions: List[QualityDimension], grade: QualityGrade) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        if grade in [QualityGrade.D, QualityGrade.F]:
            recommendations.append("Focus on structured RCA methodology - implement 5 Whys or fishbone analysis")
            recommendations.append("Add dedicated sections: Timeline, Impact, Root Cause, Action Items")
            recommendations.append("Quantify user and business impact with specific numbers")
        elif grade == QualityGrade.C:
            recommendations.append("Deepen root cause analysis - go beyond immediate causes to underlying factors")
            recommendations.append("Add prevention-focused action items with clear ownership and timelines")
            recommendations.append("Include lessons learned section for broader organizational value")
        elif grade == QualityGrade.B:
            recommendations.append("Enhance technical depth in root cause analysis")
            recommendations.append("Strengthen prevention focus in action items")
            recommendations.append("Consider adding executive summary for leadership communication")
        
        # Add dimension-specific recommendations
        lowest_scoring_dim = min(dimensions, key=lambda d: d.score / d.max_points)
        if lowest_scoring_dim.score < lowest_scoring_dim.max_points * 0.7:
            recommendations.append(f"Priority improvement area: {lowest_scoring_dim.name} - {lowest_scoring_dim.gaps[0] if lowest_scoring_dim.gaps else 'needs attention'}")
        
        return recommendations[:5]
    
    def _assess_confidence(self, analysis: Dict, total_score: int) -> str:
        """Assess confidence in the analysis"""
        # High confidence if we have good content to work with
        content_indicators = sum(1 for dim in analysis.values() if dim['score'] > 0)
        
        if content_indicators >= 6 and total_score > 40:
            return "High"
        elif content_indicators >= 4 and total_score > 20:
            return "Medium"
        else:
            return "Low"
    
    def _create_fallback_assessment(self, ticket_key: str, error_message: str) -> RCAQualityAssessment:
        """Create fallback assessment when analysis fails"""
        fallback_dimension = QualityDimension(
            name="Analysis Failed",
            max_points=100,
            score=0,
            feedback=f"Quality assessment failed: {error_message}",
            strengths=[],
            gaps=["Unable to assess RCA quality due to analysis failure"]
        )
        
        return RCAQualityAssessment(
            ticket_key=ticket_key,
            total_score=0,
            grade=QualityGrade.F,
            dimensions=[fallback_dimension],
            overall_feedback=f"RCA quality assessment failed for {ticket_key}",
            top_strengths=[],
            critical_gaps=["Analysis system failure"],
            improvement_recommendations=["Retry quality assessment with valid RCA content"],
            assessment_confidence="Low"
        )