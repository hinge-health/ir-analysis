#!/usr/bin/env python3
"""
Incident Analysis Tool
Extract incident data from Jira and match with Confluence RCA documents
"""

import os
import sys
import logging
import argparse
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jira_client import JiraClient
from confluence_client import ConfluenceClient
from rca_analyzer import RCAAnalyzer
from rca_quality_analyzer import RCAQualityAnalyzer
from business_impact_analyzer import BusinessImpactAnalyzer
from technical_analyzer import TechnicalAnalyzer
from json_exporter import IncidentJSONExporter

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

def analyze_rca_content(incidents: List[Dict], confluence_client: ConfluenceClient, rca_analyzer: RCAAnalyzer, 
                       quality_analyzer: RCAQualityAnalyzer, business_analyzer: BusinessImpactAnalyzer, 
                       technical_analyzer: TechnicalAnalyzer, preserve_html: bool = False) -> List[Dict]:
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
        
        # Initialize quality assessment fields with defaults
        incident['rca_quality_score'] = 0
        incident['rca_grade'] = 'N/A'
        incident['quality_feedback'] = 'RCA document not available for quality assessment'
        incident['strengths_identified'] = 'N/A'
        incident['critical_gaps'] = 'N/A'
        
        # Initialize business impact fields with defaults (Phase 6)
        incident['business_impact_score'] = 1
        incident['customer_count_affected'] = 'Not specified'
        incident['revenue_impact_est'] = 'Unable to estimate'
        incident['service_downtime_minutes'] = 0
        incident['severity_justification'] = 'RCA document not available'
        
        # Initialize technical analysis fields with defaults (Phase 6)
        incident['root_cause_category'] = 'Unknown'
        incident['detection_time_minutes'] = 0
        incident['resolution_time_minutes'] = 0
        incident['technical_debt_level'] = 'Unknown'
        incident['automation_score'] = 0
        
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
            
            # Preserve HTML content for JSON export if requested
            if preserve_html:
                incident['rca_content_html'] = rca_content_data['content_html']
                incident['rca_title'] = rca_content_data.get('title', '')
            
            # Clean HTML content for analysis
            cleaned_content = confluence_client.clean_html_content(
                rca_content_data['content_html']
            )
            
            # Preserve cleaned text content for JSON export
            if preserve_html:
                incident['rca_content_text'] = cleaned_content
            
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
            
            # Perform quality assessment if content analysis was successful
            try:
                quality_assessment = quality_analyzer.analyze_rca_quality(cleaned_content, ticket_key)
                
                # Update incident with quality assessment results
                incident['rca_quality_score'] = quality_assessment.total_score
                incident['rca_grade'] = quality_assessment.grade.value
                incident['quality_feedback'] = quality_assessment.overall_feedback
                incident['strengths_identified'] = '; '.join(quality_assessment.top_strengths) if quality_assessment.top_strengths else 'None identified'
                incident['critical_gaps'] = '; '.join(quality_assessment.critical_gaps) if quality_assessment.critical_gaps else 'None identified'
                
                logger.debug(f"Quality assessment for {ticket_key}: {quality_assessment.grade.value} ({quality_assessment.total_score}/100)")
                
            except Exception as quality_error:
                logger.warning(f"Quality assessment failed for {ticket_key}: {str(quality_error)}")
                incident['quality_feedback'] = f'Quality assessment failed: {str(quality_error)}'
            
            # Perform business impact analysis (Phase 6)
            try:
                business_impact = business_analyzer.analyze_business_impact(
                    cleaned_content, ticket_key, incident.get('incident_urgency', 'P4'),
                    incident.get('summary', ''), incident.get('pods_engaged', '')
                )
                
                # Update incident with business impact results
                incident['business_impact_score'] = business_impact.impact_score
                incident['customer_count_affected'] = business_impact.customer_count_affected
                incident['revenue_impact_est'] = business_impact.revenue_impact_est
                incident['service_downtime_minutes'] = business_impact.service_downtime_minutes
                incident['severity_justification'] = business_impact.severity_justification
                
                logger.debug(f"Business impact for {ticket_key}: Score {business_impact.impact_score}/10")
                
            except Exception as business_error:
                logger.warning(f"Business impact analysis failed for {ticket_key}: {str(business_error)}")
                incident['severity_justification'] = f'Business analysis failed: {str(business_error)}'
            
            # Perform technical analysis (Phase 6)
            try:
                technical_analysis = technical_analyzer.analyze_technical_aspects(
                    cleaned_content, ticket_key, incident.get('created', '')
                )
                
                # Update incident with technical analysis results
                incident['root_cause_category'] = technical_analysis.root_cause_category
                incident['detection_time_minutes'] = technical_analysis.detection_time_minutes
                incident['resolution_time_minutes'] = technical_analysis.resolution_time_minutes
                incident['technical_debt_level'] = technical_analysis.technical_debt_level
                incident['automation_score'] = technical_analysis.automation_score
                
                logger.debug(f"Technical analysis for {ticket_key}: {technical_analysis.root_cause_category}, Automation: {technical_analysis.automation_score}/5")
                
            except Exception as tech_error:
                logger.warning(f"Technical analysis failed for {ticket_key}: {str(tech_error)}")
                incident['root_cause_category'] = f'Analysis failed: {str(tech_error)}'
            
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
    
    # Prepare data for DataFrame - Phase 6 Dual-Audience Structure (22 columns)
    report_data = []
    for incident in incidents:
        report_data.append({
            # Core Incident Data (7 columns)
            'Ticket Key': incident.get('ticket_key'),
            'Summary': incident.get('summary'),
            'Priority': incident.get('incident_urgency', 'TBD'),
            'Created Date': incident.get('created'),
            'Status': incident.get('status'),
            'Teams Involved': incident.get('pods_engaged', 'TBD'),
            'RCA Link': incident.get('rca_link', 'Not Found'),
            
            # Business Impact Analysis (5 columns) - For Leadership
            'Business Impact Score': incident.get('business_impact_score', 1),
            'Customer Count Affected': incident.get('customer_count_affected', 'Not specified'),
            'Revenue Impact Est': incident.get('revenue_impact_est', 'Unable to estimate'),
            'Service Downtime Minutes': incident.get('service_downtime_minutes', 0),
            'Severity Justification': incident.get('severity_justification', 'Not analyzed'),
            
            # Technical Analysis (5 columns) - For IC Engineers
            'Root Cause Category': incident.get('root_cause_category', 'Unknown'),
            'Detection Time Minutes': incident.get('detection_time_minutes', 0),
            'Resolution Time Minutes': incident.get('resolution_time_minutes', 0),
            'Technical Debt Level': incident.get('technical_debt_level', 'Unknown'),
            'Automation Score': incident.get('automation_score', 0),
            
            # Quality Assessment (5 columns) - For Both Audiences
            'RCA Quality Score': incident.get('rca_quality_score', 0),
            'RCA Grade': incident.get('rca_grade', 'N/A'),
            'Quality Feedback': incident.get('quality_feedback', 'Not assessed'),
            'Top 2 Strengths': incident.get('strengths_identified', 'N/A'),
            'Top 2 Critical Gaps': incident.get('critical_gaps', 'N/A')
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
    
    # Quality assessment statistics
    quality_assessed = len([i for i in incidents if i.get('rca_grade') and i.get('rca_grade') != 'N/A'])
    grade_a = len([i for i in incidents if i.get('rca_grade') == 'A'])
    grade_b = len([i for i in incidents if i.get('rca_grade') == 'B'])
    grade_c = len([i for i in incidents if i.get('rca_grade') == 'C'])
    grade_d = len([i for i in incidents if i.get('rca_grade') == 'D'])
    grade_f = len([i for i in incidents if i.get('rca_grade') == 'F'])
    
    # Calculate average quality score (recalibrated in Phase 6)
    quality_scores = [i.get('rca_quality_score', 0) for i in incidents if i.get('rca_quality_score', 0) > 0]
    avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Business impact statistics (Phase 6)
    business_scores = [i.get('business_impact_score', 1) for i in incidents if i.get('business_impact_score', 1) > 1]
    avg_business_impact = sum(business_scores) / len(business_scores) if business_scores else 1
    high_impact = len([i for i in incidents if i.get('business_impact_score', 1) >= 7])
    total_downtime = sum([i.get('service_downtime_minutes', 0) for i in incidents])
    
    # Technical analysis statistics (Phase 6)
    automation_scores = [i.get('automation_score', 0) for i in incidents if i.get('automation_score', 0) > 0]
    avg_automation_score = sum(automation_scores) / len(automation_scores) if automation_scores else 0
    detection_times = [i.get('detection_time_minutes', 0) for i in incidents if i.get('detection_time_minutes', 0) > 0]
    avg_detection_time = sum(detection_times) / len(detection_times) if detection_times else 0
    resolution_times = [i.get('resolution_time_minutes', 0) for i in incidents if i.get('resolution_time_minutes', 0) > 0]
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    logger.info(f"Phase 6 Enhanced Report Summary:")
    logger.info(f"  Total incidents: {total_incidents}")
    logger.info(f"  With RCA documents: {with_rca} ({with_rca/total_incidents*100:.1f}%)")
    logger.info(f"  RCA documents analyzed: {analyzed_rca} ({analyzed_rca/total_incidents*100:.1f}%)")
    logger.info(f"  ")
    logger.info(f"  QUALITY METRICS (Recalibrated):")
    logger.info(f"    Grade distribution: A={grade_a} ({grade_a/total_incidents*100:.1f}%), B={grade_b} ({grade_b/total_incidents*100:.1f}%), C={grade_c} ({grade_c/total_incidents*100:.1f}%), D={grade_d}, F={grade_f}")
    logger.info(f"    Average quality score: {avg_quality_score:.1f}/100")
    logger.info(f"  ")
    logger.info(f"  BUSINESS IMPACT METRICS:")
    logger.info(f"    High-impact incidents (7-10/10): {high_impact} ({high_impact/total_incidents*100:.1f}%)")
    logger.info(f"    Average business impact score: {avg_business_impact:.1f}/10")
    logger.info(f"    Total service downtime: {total_downtime} minutes")
    logger.info(f"  ")
    logger.info(f"  TECHNICAL METRICS:")
    logger.info(f"    Average detection time: {avg_detection_time:.1f} minutes")
    logger.info(f"    Average resolution time: {avg_resolution_time:.1f} minutes")
    logger.info(f"    Average automation opportunity score: {avg_automation_score:.1f}/5")
    logger.info(f"  ")
    logger.info(f"  Missing RCA documents: {total_incidents - with_rca}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Incident Analysis Tool - Extract and analyze incident data from Jira and Confluence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                              # Standard CSV export
  python main.py --json-export                # Export JSON with all data
  python main.py --json-export --recent 10    # Export JSON for 10 most recent incidents
  python main.py --json-export --since 2024-01-15  # Export incidents since specific date
  python main.py --json-export --output-json /path/to/output.json  # Custom JSON output path
        """
    )
    
    # Output format options
    parser.add_argument('--json-export', action='store_true',
                       help='Export data as JSON instead of CSV (includes full RCA content)')
    
    parser.add_argument('--output-json', type=str,
                       help='Path for JSON output file (default: auto-generated)')
    
    # Filtering options
    parser.add_argument('--recent', type=int, metavar='N',
                       help='Export only the N most recent incidents')
    
    parser.add_argument('--since', type=str, metavar='YYYY-MM-DD',
                       help='Export incidents since specific date (format: YYYY-MM-DD)')
    
    # Standard options
    parser.add_argument('--output-csv', type=str,
                       help='Path for CSV output file (default: auto-generated)')
    
    return parser.parse_args()

def filter_incidents_by_date(incidents: List[Dict], since_date: str) -> List[Dict]:
    """Filter incidents to only include those since the specified date"""
    logger = logging.getLogger(__name__)
    
    try:
        cutoff_date = datetime.strptime(since_date, '%Y-%m-%d')
        logger.info(f"Filtering incidents since {since_date}")
        
        filtered_incidents = []
        for incident in incidents:
            created_str = incident.get('created', '')
            if created_str:
                try:
                    # Parse various date formats that might come from Jira
                    created_date = None
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d']:
                        try:
                            created_date = datetime.strptime(created_str.split('.')[0].replace('Z', '+00:00'), fmt.replace('%f', '').replace('%z', ''))
                            break
                        except ValueError:
                            continue
                    
                    if created_date and created_date >= cutoff_date:
                        filtered_incidents.append(incident)
                        
                except Exception as e:
                    logger.warning(f"Could not parse date for {incident.get('ticket_key', 'UNKNOWN')}: {created_str}")
                    continue
        
        logger.info(f"Filtered {len(incidents)} incidents to {len(filtered_incidents)} since {since_date}")
        return filtered_incidents
        
    except ValueError as e:
        logger.error(f"Invalid date format '{since_date}'. Please use YYYY-MM-DD format.")
        raise

def filter_recent_incidents(incidents: List[Dict], count: int) -> List[Dict]:
    """Filter to get the N most recent incidents"""
    logger = logging.getLogger(__name__)
    
    # Sort incidents by created date (most recent first)
    def parse_date(incident):
        created_str = incident.get('created', '')
        if not created_str:
            return datetime.min
        
        try:
            # Parse date string - handle various formats
            for fmt in ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d']:
                try:
                    return datetime.strptime(created_str.split('.')[0].replace('Z', '+00:00'), fmt.replace('%f', '').replace('%z', ''))
                except ValueError:
                    continue
            return datetime.min
        except Exception:
            return datetime.min
    
    sorted_incidents = sorted(incidents, key=parse_date, reverse=True)
    filtered_incidents = sorted_incidents[:count]
    
    logger.info(f"Filtered to {len(filtered_incidents)} most recent incidents (from {len(incidents)} total)")
    return filtered_incidents

def main():
    """Main execution function"""
    # Parse command line arguments
    args = parse_arguments()
    
    logger = setup_logging()
    logger.info("Starting Incident Analysis Tool")
    
    if args.json_export:
        logger.info("JSON export mode enabled")
    if args.recent:
        logger.info(f"Filtering to {args.recent} most recent incidents")
    if args.since:
        logger.info(f"Filtering incidents since {args.since}")
    
    try:
        # Initialize clients and analyzers (Phase 7 enhanced)
        logger.info("Initializing API clients and analyzers...")
        jira_client = JiraClient()
        confluence_client = ConfluenceClient()
        rca_analyzer = RCAAnalyzer()
        quality_analyzer = RCAQualityAnalyzer()
        business_analyzer = BusinessImpactAnalyzer()
        technical_analyzer = TechnicalAnalyzer()
        
        # Initialize JSON exporter if needed
        json_exporter = IncidentJSONExporter() if args.json_export else None
        
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
        
        # Apply filtering if requested
        original_count = len(incidents)
        export_type = "full"
        date_range = None
        
        if args.since:
            incidents = filter_incidents_by_date(incidents, args.since)
            export_type = f"since_{args.since}"
            date_range = f"{args.since} to present"
        
        if args.recent:
            incidents = filter_recent_incidents(incidents, args.recent)
            export_type = f"recent_{args.recent}"
            if not date_range:
                # Calculate date range from filtered incidents
                if incidents:
                    dates = [i.get('created', '') for i in incidents if i.get('created')]
                    if dates:
                        dates.sort()
                        date_range = f"{dates[0].split('T')[0]} to {dates[-1].split('T')[0]}"
        
        logger.info(f"Processing {len(incidents)} incidents (filtered from {original_count})")
        
        if not incidents:
            logger.error("No incidents found after filtering!")
            return 1
        
        # Match with RCA documents
        incidents = match_rca_documents(incidents, confluence_client)
        
        # Analyze RCA content (Phase 7 enhanced - preserve HTML for JSON export)
        preserve_html = args.json_export
        incidents = analyze_rca_content(incidents, confluence_client, rca_analyzer, quality_analyzer, 
                                       business_analyzer, technical_analyzer, preserve_html)
        
        # Generate output
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if args.json_export:
            # JSON export
            if args.output_json:
                json_output_file = args.output_json
            else:
                json_output_file = os.path.join(output_dir, f'incidents_data_{export_type}_{timestamp}.json')
            
            json_exporter.export_incidents_json(incidents, json_output_file, export_type, date_range)
            logger.info(f"JSON export completed: {json_output_file}")
        else:
            # Standard CSV export
            if args.output_csv:
                csv_output_file = args.output_csv
            else:
                csv_output_file = os.path.join(output_dir, f'incidents_2024_enhanced_{timestamp}.csv')
            
            generate_csv_report(incidents, csv_output_file)
            logger.info(f"CSV export completed: {csv_output_file}")
        
        logger.info("Incident analysis completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())