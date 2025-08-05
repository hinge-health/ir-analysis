#!/usr/bin/env python3
"""
JSON Data Exporter for Incident Analysis

Exports comprehensive incident and RCA data as structured JSON
optimized for LLM analysis and custom processing.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import asdict

class IncidentJSONExporter:
    """Exports incident data to structured JSON format for LLM analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_incidents_json(self, incidents: List[Dict], output_file: str, 
                             export_type: str = "full", date_range: str = None) -> None:
        """
        Export incidents to structured JSON format optimized for LLM analysis
        
        Args:
            incidents: List of incident data dictionaries
            output_file: Path to output JSON file
            export_type: Type of export (full, recent_N, date_range)
            date_range: Date range string for metadata
        """
        self.logger.info(f"Exporting {len(incidents)} incidents to JSON: {output_file}")
        
        # Create comprehensive JSON structure
        json_data = {
            "export_metadata": self._create_export_metadata(incidents, export_type, date_range),
            "incidents": []
        }
        
        # Process each incident
        for incident in incidents:
            try:
                incident_json = self._create_incident_json(incident)
                json_data["incidents"].append(incident_json)
            except Exception as e:
                self.logger.warning(f"Failed to export incident {incident.get('ticket_key', 'UNKNOWN')}: {str(e)}")
                continue
        
        # Write JSON file with proper formatting
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            
            self.logger.info(f"Successfully exported {len(json_data['incidents'])} incidents to {output_file}")
            
            # Log summary statistics
            self._log_export_summary(json_data)
            
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {output_file}: {str(e)}")
            raise
    
    def _create_export_metadata(self, incidents: List[Dict], export_type: str, 
                               date_range: str) -> Dict[str, Any]:
        """Create export metadata section"""
        
        total_incidents = len(incidents)
        with_rca = len([i for i in incidents if i.get('rca_link') and i.get('rca_link') != 'Not Found'])
        analyzed_rca = len([i for i in incidents if i.get('analysis_quality') and i.get('analysis_quality') != 'N/A'])
        
        # Get date range from actual data if not provided
        if not date_range and incidents:
            dates = [i.get('created') for i in incidents if i.get('created')]
            if dates:
                dates.sort()
                date_range = f"{dates[0]} to {dates[-1]}"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_incidents": total_incidents,
            "incidents_with_rca": with_rca,
            "rca_analyzed_count": analyzed_rca,
            "date_range": date_range or "Unknown",
            "export_type": export_type,
            "rca_match_rate": f"{with_rca/total_incidents*100:.1f}%" if total_incidents > 0 else "0%",
            "analysis_success_rate": f"{analyzed_rca/with_rca*100:.1f}%" if with_rca > 0 else "0%",
            "schema_version": "1.0",
            "purpose": "LLM analysis and custom processing"
        }
    
    def _create_incident_json(self, incident: Dict) -> Dict[str, Any]:
        """Create comprehensive JSON structure for a single incident"""
        
        return {
            "jira_data": {
                "ticket_key": incident.get('ticket_key'),
                "summary": incident.get('summary'),
                "priority": incident.get('incident_urgency', 'TBD'),
                "created_date": incident.get('created'),
                "status": incident.get('status'),
                "description": incident.get('description', ''),
                "custom_fields": {
                    "incident_urgency": incident.get('incident_urgency'),
                    "pods_engaged": incident.get('pods_engaged'),
                    "reporter": incident.get('reporter'),
                    "assignee": incident.get('assignee')
                },
                "comments": incident.get('comments', []),
                "metadata": {
                    "jira_url": f"https://hingehealth.atlassian.net/browse/{incident.get('ticket_key')}" if incident.get('ticket_key') else None,
                    "labels": incident.get('labels', []),
                    "component": incident.get('component'),
                    "resolution": incident.get('resolution')
                }
            },
            "confluence_data": {
                "rca_url": incident.get('rca_link'),
                "rca_available": incident.get('rca_link') not in [None, 'Not Found', ''],
                "content_html": incident.get('rca_content_html', ''),
                "content_text": incident.get('rca_content_text', ''),
                "title": incident.get('rca_title', ''),
                "page_metadata": {
                    "space": "RND",
                    "page_id": self._extract_page_id(incident.get('rca_link', '')),
                    "estimated_word_count": len(incident.get('rca_content_text', '').split()) if incident.get('rca_content_text') else 0
                }
            },
            "analysis_results": {
                "content_analysis": {
                    "incident_summary": incident.get('rca_summary', ''),
                    "users_impacted": incident.get('users_impacted', ''),
                    "root_causes": incident.get('root_causes', '').split('; ') if incident.get('root_causes') else [],
                    "analysis_quality": incident.get('analysis_quality', 'N/A')
                },
                "quality_assessment": {
                    "score": incident.get('rca_quality_score', 0),
                    "grade": incident.get('rca_grade', 'N/A'),
                    "feedback": incident.get('quality_feedback', ''),
                    "strengths": incident.get('strengths_identified', '').split('; ') if incident.get('strengths_identified') else [],
                    "critical_gaps": incident.get('critical_gaps', '').split('; ') if incident.get('critical_gaps') else []
                },
                "business_impact": {
                    "impact_score": incident.get('business_impact_score', 1),
                    "customer_count_affected": incident.get('customer_count_affected', ''),
                    "revenue_impact_est": incident.get('revenue_impact_est', ''),
                    "service_downtime_minutes": incident.get('service_downtime_minutes', 0),
                    "severity_justification": incident.get('severity_justification', '')
                },
                "technical_analysis": {
                    "root_cause_category": incident.get('root_cause_category', 'Unknown'),
                    "detection_time_minutes": incident.get('detection_time_minutes', 0),
                    "resolution_time_minutes": incident.get('resolution_time_minutes', 0),
                    "technical_debt_level": incident.get('technical_debt_level', 'Unknown'),
                    "automation_score": incident.get('automation_score', 0)
                }
            }
        }
    
    def _extract_page_id(self, rca_url: str) -> Optional[str]:
        """Extract Confluence page ID from RCA URL"""
        if not rca_url or rca_url == 'Not Found':
            return None
        
        try:
            # Extract page ID from URL pattern: .../pages/123456789/...
            import re
            match = re.search(r'/pages/(\d+)/', rca_url)
            return match.group(1) if match else None
        except Exception:
            return None
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for special objects"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'value'):  # For Enum objects
            return obj.value
        return str(obj)
    
    def _log_export_summary(self, json_data: Dict) -> None:
        """Log summary statistics of the export"""
        metadata = json_data["export_metadata"]
        incidents = json_data["incidents"]
        
        # Count various data completeness metrics
        with_html_content = len([i for i in incidents if i['confluence_data']['content_html']])
        with_analysis = len([i for i in incidents if i['analysis_results']['content_analysis']['analysis_quality'] != 'N/A'])
        with_quality_scores = len([i for i in incidents if i['analysis_results']['quality_assessment']['score'] > 0])
        
        self.logger.info("JSON Export Summary:")
        self.logger.info(f"  Export metadata: {metadata['export_type']} - {metadata['date_range']}")
        self.logger.info(f"  Total incidents: {metadata['total_incidents']}")
        self.logger.info(f"  RCA documents found: {metadata['incidents_with_rca']} ({metadata['rca_match_rate']})")
        self.logger.info(f"  RCA content available: {with_html_content}")
        self.logger.info(f"  Content analysis complete: {with_analysis}")
        self.logger.info(f"  Quality assessments: {with_quality_scores}")
        self.logger.info(f"  Analysis success rate: {metadata['analysis_success_rate']}")
        
        # Data completeness breakdown
        avg_content_length = sum([len(i['confluence_data']['content_text']) for i in incidents]) / len(incidents) if incidents else 0
        self.logger.info(f"  Average RCA content length: {avg_content_length:.0f} characters")
        
        # Quality distribution
        grades = [i['analysis_results']['quality_assessment']['grade'] for i in incidents]
        grade_counts = {grade: grades.count(grade) for grade in ['A', 'B', 'C', 'D', 'F']}
        self.logger.info(f"  Quality grade distribution: {grade_counts}")
    