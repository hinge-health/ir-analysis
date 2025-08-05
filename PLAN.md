# Incident Analysis Project Plan

## Project Overview
Build a system to pull incident data from Jira and Confluence to analyze company incidents registered on the IR (Incident Recovery) board since January 1, 2024.

## Data Sources & Requirements

### Jira Configuration
- **Project**: IR (Incident Recovery board)
- **Date Filter**: Created since January 1, 2024
- **Status Exclusions**: "Duplicate", "Not an Incident"
- **JQL Query**: `project = IR and created > '2024-01-01' and status not in (Duplicate, "Not an Incident")`

### Key Jira Fields
- **Ticket Key**: Primary identifier
- **Summary**: Incident title
- **Incident Urgency**: Custom field (P1-P4 priority)
- **Description**: Jira ticket description
- **Pods Engaged**: Custom field identifying involved teams
- **Comments**: Source for RCA document links (posted by "Automation for Jira")

### Confluence Integration
- **Location**: RND/Incident Response/RCA Documents
- **Naming Convention**: Pages start with "RCA IR-XXX" (matching Jira ticket key)
- **Link Source**: Found in Jira comments by "Automation for Jira"
- **Example**: https://hingehealth.atlassian.net/wiki/spaces/RND/pages/1521615193/RCA+IR-360+App+crashing+on+android

## Recommended Tech Stack

### Primary Option: Python
**Rationale**: Excellent SDK support, data processing capabilities, CSV generation

**Key Libraries**:
- `atlassian-python-api`: Comprehensive Jira & Confluence SDK
- `pandas`: Data manipulation and CSV export
- `requests`: HTTP client for API calls
- `python-dotenv`: Environment variable management
- `logging`: Built-in logging for debugging

**Advantages**:
- Mature Atlassian SDKs with extensive documentation
- Strong data processing ecosystem
- Easy CSV generation
- Excellent error handling and logging
- Large community support

### Alternative Option: Node.js
**Libraries**: `jira-client`, `confluence-api`, `csv-writer`

## Implementation Phases

### Phase 1: Data Verification
**Objective**: Verify data access and availability
**Tasks**:
1. Set up authentication for Jira and Confluence APIs
2. Test connection to IR project in Jira
3. Retrieve and validate incident count since Jan 1, 2024
4. Verify exclusion of "Duplicate" and "Not an Incident" statuses
5. Test access to Confluence RCA documents space

### Phase 2: RCA Document Matching
**Objective**: Establish reliable RCA document discovery
**Tasks**:
1. Parse Jira comments to find RCA links from "Automation for Jira"
2. Implement Confluence search by RCA naming convention
3. Create fallback strategy for missing RCA documents
4. Validate RCA matching for sample incidents

### Phase 3: Data Extraction & CSV Generation
**Objective**: Generate comprehensive incident report
**Tasks**:
1. Extract all required Jira fields
2. Match and retrieve RCA document links
3. Generate CSV with specified columns:
   - Ticket Key
   - Summary
   - Incident Urgency
   - Jira Description
   - RCA Link
   - Pods Engaged (bonus field)

### Phase 4: RCA Content Analysis (NEW FEATURE)
**Objective**: Extract detailed insights from RCA documents using LLM analysis
**Tasks**:
1. Retrieve RCA document content from Confluence
2. Implement LLM-based content analysis
3. Extract structured data from RCA documents:
   - **Incident Summary**: 1-paragraph executive summary
   - **Users Impacted**: Number/type of affected users
   - **Root Causes**: Primary and contributing factors
4. Add new columns to CSV output
5. Generate analysis quality metrics

**LLM Analysis Options**:
- **Option 1**: Claude Code built-in analysis (Recommended)
- **Option 2**: OpenAI API integration
- **Option 3**: Local LLM (ollama/llamacpp)

### Phase 5: RCA Quality Assessment & Process Improvement ✅ **COMPLETED**
**Objective**: Evaluate RCA document quality against engineering best practices and provide actionable feedback for process improvement
**Tasks**:
1. **Expert RCA Quality Analyzer**: Implement LLM-powered quality assessment using engineering best practices ✅
2. **Comprehensive Grading System**: Score RCAs on 7 key dimensions (0-100 scale, A-F grades) ✅
3. **Gap Analysis & Feedback**: Provide specific, actionable improvement recommendations ✅
4. **Quality Metrics Dashboard**: Generate aggregate quality insights across teams/incident types ✅
5. **Process Improvement Recommendations**: Identify systemic patterns and suggest RCA process enhancements ✅

**Quality Assessment Dimensions**:
- **Timeline & Detection (15 pts)**: Clear incident timeline, detection methods, response efficiency
- **Impact Assessment (15 pts)**: User/business impact quantification, scope definition
- **Root Cause Analysis (25 pts)**: Depth of analysis, methodology usage (5 Whys, fishbone), technical accuracy
- **Communication & Clarity (10 pts)**: Document structure, clarity, audience-appropriate communication
- **Action Items & Prevention (20 pts)**: Specific remediation actions, ownership, timelines, prevention focus
- **Process Adherence (10 pts)**: Follows structured incident response methodology
- **Learning & Knowledge Sharing (5 pts)**: Extractable lessons, knowledge transfer value

**Enhanced CSV Outputs**:
- **RCA Quality Score**: Numerical assessment (0-100) ✅
- **RCA Grade**: Letter grade (A, B, C, D, F) ✅
- **Quality Feedback**: Specific improvement recommendations ✅
- **Strengths Identified**: What the RCA did exceptionally well ✅
- **Critical Gaps**: Most important areas for improvement ✅

**Results**: 91/91 RCA documents assessed, average quality score 90.6/100, grade distribution A=61, B=23, C=7

### Phase 6: Dual-Audience CSV Optimization & Enhanced Analytics
**Objective**: Optimize CSV structure and analytics for both IC engineers and engineering leadership (CTO-level) with improved scoring calibration and business impact analysis
**Tasks**:
1. **Scoring Recalibration**: Implement more critical assessment to achieve realistic grade distribution (target: A=15%, B=30%, C=40%, D=15%)
2. **Dual-Audience Structure**: Create CSV optimized for both technical teams and executive leadership
3. **Business Impact Analytics**: Add quantified business impact, customer impact, and revenue estimation columns
4. **Technical Analysis Enhancement**: Add technical categorization, detection/resolution times, automation opportunities
5. **Enhanced Feedback System**: Replace generic feedback with specific, actionable recommendations
6. **Leadership Dashboard Metrics**: Add executive-level KPIs and trend analysis

**New CSV Structure (22 columns)**:

**Core Incident Data (7 columns)**:
- Ticket_Key, Summary, Priority, Created_Date, Status, Teams_Involved, RCA_Link

**Business Impact Analysis (5 columns)**:
- Business_Impact_Score (1-10), Customer_Count_Affected, Revenue_Impact_Est, Service_Downtime_Minutes, Severity_Justification

**Technical Analysis (5 columns)**:
- Root_Cause_Category, Detection_Time_Minutes, Resolution_Time_Minutes, Technical_Debt_Level, Automation_Score (0-5)

**Quality Assessment (5 columns)**:
- RCA_Quality_Score (recalibrated), RCA_Grade (stricter), Quality_Category_Breakdown, Top_2_Strengths, Top_2_Critical_Gaps

**Enhanced Quality Feedback**:
- Specific, actionable feedback replacing generic responses
- Business impact focus for leadership visibility
- Technical depth analysis for IC engineers
- Prevention-focused recommendations with ownership

**Leadership KPIs**:
- Team_RCA_Quality_Trend, Prevention_Success_Rate, Mean_Time_To_Detection_By_Team
- High_Impact_Incident_Rate, Incident_Learning_Velocity

## Project Structure
```
incident-analysis/
├── src/
│   ├── jira_client.py          # Jira API integration
│   ├── confluence_client.py    # Confluence API integration
│   ├── rca_analyzer.py         # LLM-based RCA content analysis
│   ├── rca_quality_analyzer.py # Expert RCA quality assessment & grading
│   ├── data_processor.py       # Data extraction & processing
│   └── main.py                 # Main execution script
├── config/
│   ├── .env.example           # Environment variables template
│   └── requirements.txt       # Python dependencies
├── output/                    # Generated CSV files
├── logs/                      # Application logs
├── PLAN.md                    # This file
└── README.md                  # Setup and usage instructions
```

## Configuration Requirements

### Environment Variables
```
JIRA_URL=https://hingehealth.atlassian.net
CONFLUENCE_URL=https://hingehealth.atlassian.net/wiki
ATLASSIAN_EMAIL=your-email@hingehealth.com
ATLASSIAN_API_TOKEN=your-api-token
```

### API Permissions Required
- **Jira**: Read access to IR project and custom fields
- **Confluence**: Read access to RND space and RCA documents

## Expected Deliverables
1. **incidents_2024_enhanced.csv**: Complete incident data with RCA analysis since Jan 1, 2024
2. **rca_analysis_summary.json**: Detailed RCA analysis results for review
3. **data_quality_report.txt**: Summary of data completeness and analysis quality
4. **execution_log**: Detailed processing log for troubleshooting

## Success Criteria
- ✅ Successfully retrieve all IR incidents since Jan 1, 2024
- ✅ Exclude duplicate and non-incident tickets
- ✅ Match ≥95% of incidents to their RCA documents
- ✅ Generate clean CSV with all required columns including RCA analysis
- ✅ Successfully analyze ≥90% of available RCA documents with LLM
- ✅ Extract structured incident summaries, user impact, and root causes
- ✅ **Phase 5**: Evaluate RCA quality using expert-level assessment criteria
- ✅ **Phase 5**: Generate actionable quality improvement recommendations
- ✅ **Phase 5**: Provide aggregate quality metrics and process improvement insights
- 🆕 **Phase 6**: Implement dual-audience CSV structure for IC engineers and leadership
- 🆕 **Phase 6**: Recalibrate quality scoring for realistic grade distribution
- 🆕 **Phase 6**: Add business impact analysis and technical categorization
- 🆕 **Phase 6**: Enhance feedback system with specific, actionable recommendations
- ✅ Handle API errors gracefully with proper logging

## RCA Content Analysis Implementation

### LLM Analysis Strategy (Recommended: Claude Code)
**Why Claude Code**: Built-in, no additional API costs, excellent at document analysis, already integrated

### Content Extraction Process
1. **Confluence API**: Retrieve RCA document content as HTML/markdown
2. **Content Preprocessing**: Clean HTML, extract main content, remove navigation
3. **LLM Analysis**: Use structured prompt to extract key information
4. **Data Validation**: Validate and clean extracted data
5. **CSV Integration**: Add analysis results as new columns

### Analysis Prompt Template
```
Analyze this Root Cause Analysis document and extract the following information in JSON format:

INCIDENT SUMMARY: Provide a 1-paragraph executive summary (2-3 sentences) of what happened, when, and the business impact.

USERS IMPACTED: Extract the number and type of users affected. Look for:
- Specific user counts (e.g., "1,200 users", "15% of members")
- User segments (e.g., "PT users", "new members", "iOS users")
- Impact duration (e.g., "30 minutes", "2 hours")

ROOT CAUSES: Identify primary and contributing root causes. Look for:
- Technical root causes (code bugs, infrastructure failures, configuration issues)
- Process root causes (deployment issues, monitoring gaps, human error)
- Environmental factors (third-party services, network issues)

Format as JSON:
{
  "incident_summary": "...",
  "users_impacted": "...",
  "root_causes": ["primary cause", "contributing cause 1", "contributing cause 2"]
}

RCA Document Content:
[DOCUMENT_CONTENT]
```

### Enhanced CSV Columns
**Existing**: Ticket Key, Summary, Incident Urgency, Jira Description, RCA Link, Pods Engaged, Created, Status

**New RCA Analysis Columns**:
- **Incident Summary**: Executive summary from RCA analysis
- **Users Impacted**: Extracted user impact information
- **Root Causes**: Structured list of identified root causes
- **Analysis Quality**: Confidence score of LLM extraction (High/Medium/Low)

### Technical Implementation Options

#### Option 1: Claude Code Built-in (RECOMMENDED)
**Pros**: 
- No additional API costs or setup
- Excellent document analysis capabilities
- Already integrated with your environment
- Can process documents in batches

**Implementation**:
```python
def analyze_rca_content(confluence_content: str) -> dict:
    # Use Claude Code's built-in analysis capabilities
    # Process through internal analysis functions
    pass
```

#### Option 2: OpenAI API Integration
**Pros**: Specialized LLM API, structured outputs
**Cons**: Additional API costs (~$0.50-2.00 per 100 RCAs), requires API key
**Cost Estimate**: ~$20-50 for 126 documents

#### Option 3: Local LLM (Ollama/LlamaCpp)
**Pros**: No API costs, full control
**Cons**: Requires local setup, potentially lower quality analysis

### Performance Considerations
- **Rate Limiting**: Process RCAs sequentially to avoid overwhelming systems
- **Caching**: Cache analysis results to avoid re-processing
- **Error Handling**: Graceful fallback for analysis failures
- **Quality Validation**: Verify extracted data makes sense

## Risk Mitigation
- **API Rate Limits**: Implement request throttling and retry logic
- **Missing RCA Documents**: Track and report unmatched incidents
- **LLM Analysis Failures**: Implement fallback strategies and quality validation
- **Content Parsing Issues**: Handle various RCA document formats gracefully
- **Authentication Issues**: Clear setup documentation and error messages
- **Data Quality**: Validation checks and quality reporting