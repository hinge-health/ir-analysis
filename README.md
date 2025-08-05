# IR-Analysis: Incident Recovery Data Analysis Tool

A comprehensive tool for extracting and analyzing incident data from Jira and Confluence, with advanced RCA (Root Cause Analysis) content analysis capabilities.

## Overview

This tool pulls incident data from Hinge Health's IR (Incident Recovery) board in Jira, matches incidents with their corresponding RCA documents in Confluence, and provides detailed analysis including:

- **Incident Data Extraction**: Complete incident metadata, urgency levels, and team involvement
- **RCA Document Matching**: Automatic linking to Confluence RCA documents
- **Enhanced Analysis**: LLM-powered extraction of incident summaries, user impact, and root causes
- **CSV Export**: Structured data export for further analysis and reporting

## Features

### ✅ Current Features (Phase 1-3)
- **Jira Integration**: Extract all IR incidents since January 1, 2024
- **Custom Field Support**: Incident Urgency (P1-P4) and Pods Engaged
- **Confluence Integration**: Automatic RCA document discovery and linking
- **Data Quality**: 126 incidents retrieved, 72.2% RCA match rate
- **CSV Export**: Clean, structured data export

### 🚧 In Development (Phase 4-5)
- **LLM-Powered RCA Analysis**: Extract structured insights from RCA documents
- **Enhanced Data Fields**: Incident summaries, user impact metrics, root cause analysis
- **Quality Validation**: Analysis confidence scoring and validation
- **Advanced Reporting**: Comprehensive data quality and analysis reports

## Quick Start

### Prerequisites
- Python 3.8+
- Atlassian account with access to Hinge Health Jira and Confluence
- API token for Atlassian services

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ir-analysis.git
   cd ir-analysis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your Atlassian credentials
   ```

4. **Run analysis:**
   ```bash
   python src/main.py
   ```

## Configuration

Create `config/.env` with your Atlassian credentials:

```env
JIRA_URL=https://hingehealth.atlassian.net
CONFLUENCE_URL=https://hingehealth.atlassian.net/wiki
ATLASSIAN_EMAIL=your-email@hingehealth.com
ATLASSIAN_API_TOKEN=your-api-token
LOG_LEVEL=INFO
```

## Output Files

- **`output/incidents_2024_*.csv`**: Main incident data export
- **`logs/incident_analysis_*.log`**: Detailed execution logs
- **`output/rca_analysis_summary.json`**: RCA analysis results (coming soon)

## Data Schema

### Current CSV Columns
| Column | Description |
|--------|-------------|
| Ticket Key | Jira ticket identifier (IR-XXX) |
| Summary | Incident title |
| Incident Urgency | Priority level (P1-P4) |
| Jira Description | Full incident description |
| RCA Link | URL to Confluence RCA document |
| Pods Engaged | Teams involved in incident response |
| Created | Incident creation timestamp |
| Status | Current ticket status |

### Upcoming Enhanced Columns
| Column | Description |
|--------|-------------|
| Incident Summary | LLM-generated executive summary |
| Users Impacted | Extracted user impact data |
| Root Causes | Structured root cause analysis |
| Analysis Quality | Confidence score of LLM analysis |

## Project Structure

```
ir-analysis/
├── src/
│   ├── jira_client.py          # Jira API integration
│   ├── confluence_client.py    # Confluence API integration
│   ├── rca_analyzer.py         # LLM-based RCA analysis (coming soon)
│   └── main.py                 # Main execution script
├── config/
│   ├── .env.example           # Environment template
│   └── requirements.txt       # Python dependencies
├── output/                    # Generated reports
├── logs/                      # Application logs
├── PLAN.md                    # Detailed project plan
└── README.md                  # This file
```

## Development

This project follows a phased development approach:

1. **Phase 1**: Data verification and API connectivity ✅
2. **Phase 2**: RCA document matching ✅  
3. **Phase 3**: Basic data extraction and CSV generation ✅
4. **Phase 4**: LLM-powered RCA content analysis 🚧
5. **Phase 5**: Advanced validation and reporting 🚧

See [PLAN.md](PLAN.md) for detailed implementation roadmap.

## Performance Stats

- **Incidents Retrieved**: 126 (since Jan 1, 2024)
- **RCA Match Rate**: 72.2% (91/126 incidents)
- **Execution Time**: ~2-3 minutes for full analysis
- **Success Rate**: 100% for available data

## Contributing

1. Create a feature branch from `main`
2. Make your changes with appropriate tests
3. Update documentation as needed
4. Submit a pull request

## License

Internal Hinge Health tool - not for external distribution.

## Support

For issues or questions, please create an issue in this repository or contact the development team.