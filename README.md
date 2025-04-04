# Bug Heatmap Analyzer

This project analyzes bug tickets from Linear.app and correlates them with GitHub pull requests to generate a heatmap of bug-prone files, and predicts the likelihood of bugs in new pull requests.

## System Architecture

```mermaid
C4Context
    title System Context Diagram for Bug Heatmap Analyzer

    Person(developer, "Developer", "Uses the tool to analyze bug patterns")
    System(bug_analyzer, "Bug Heatmap Analyzer", "Python application that analyzes bug patterns")
    System(linear, "Linear.app", "Issue tracking system")
    System(github, "GitHub", "Version control and pull request system")
    System(output, "Output Files", "CSV and visualization files")
    
    Rel(developer, bug_analyzer, "Runs with granularity level selection")
    Rel(bug_analyzer, linear, "Fetches bug tickets via GraphQL API")
    Rel(bug_analyzer, github, "Fetches PR data via REST API")
    Rel(bug_analyzer, output, "Generates multi-level analysis")
    Rel(bug_analyzer, developer, "Presents interactive dashboard")
```

```mermaid
C4Container
    title Container Diagram for Bug Heatmap Analyzer

    Person(developer, "Developer", "Uses the tool to analyze bug patterns")
    
    Container(main_app, "Main Application", "Python (main.py)", "Orchestrates the analysis process with configurable granularity")
    Container(linear_client, "Linear Client", "Python (linear_client.py)", "Handles API communication with Linear.app")
    Container(github_client, "GitHub Client", "Python (github_client.py)", "Manages GitHub API interactions")
    Container(code_parser, "Code Parser", "Python (code_parser.py)", "Analyzes code at multiple granularity levels")
    Container(bug_analyzer, "Bug Analyzer", "Python (analyzer.py)", "Correlates bug data and generates visualizations")
    Container(predictive_model, "Predictive Model", "Python (predictive_model.py)", "Predicts bug probability for new PRs")
    Container(dashboard, "Interactive Dashboard", "Streamlit", "Provides visualization and exploration interface")
    
    ContainerDb(linear_api, "Linear.app API", "GraphQL API")
    ContainerDb(github_api, "GitHub API", "REST API")
    ContainerDb(file_system, "File System", "Repository files and metadata")
    ContainerDb(output_files, "Output Files", "CSV, JSON, and PNG files")
    
    Rel(developer, main_app, "Runs with granularity level")
    Rel(developer, dashboard, "Explores analytics")
    
    Rel(main_app, linear_client, "Uses")
    Rel(main_app, github_client, "Uses")
    Rel(main_app, bug_analyzer, "Uses")
    Rel(main_app, dashboard, "Launches")
    
    Rel(linear_client, linear_api, "Fetches bug tickets")
    Rel(github_client, github_api, "Fetches PR data")
    
    Rel(bug_analyzer, code_parser, "Uses for granularity mapping")
    Rel(bug_analyzer, predictive_model, "Trains with historical data")
    Rel(bug_analyzer, output_files, "Generates")
    
    Rel(code_parser, file_system, "Analyzes at module/file/function/line level")
    Rel(dashboard, output_files, "Reads")
```

```mermaid
C4Component
    title Component Diagram for Code Parser and Bug Analyzer
    
    Component(parser_init, "Parser Configuration", "Loads granularity settings")
    Component(module_parser, "Module Parser", "Maps bugs to module/directory level")
    Component(file_parser, "File Parser", "Maps bugs to individual files")
    Component(function_parser, "Function Parser", "Parses code to identify functions and classes")
    Component(line_parser, "Line Parser", "Utilizes git blame data for line-level analysis")
    
    Component(analyzer_init, "Analyzer Configuration", "Sets up visualization parameters")
    Component(module_viz, "Module Visualization", "Generates treemaps for module analysis")
    Component(file_viz, "File Visualization", "Creates bar charts for file analysis")
    Component(function_viz, "Function Visualization", "Generates function-level heatmaps")
    Component(line_viz, "Line Visualization", "Creates line-level heatmaps with code context")
    
    Rel(parser_init, module_parser, "Uses if granularity=module")
    Rel(parser_init, file_parser, "Uses if granularity=file")
    Rel(parser_init, function_parser, "Uses if granularity=function")
    Rel(parser_init, line_parser, "Uses if granularity=line")
    
    Rel(analyzer_init, module_viz, "Uses if granularity=module")
    Rel(analyzer_init, file_viz, "Uses if granularity=file")
    Rel(analyzer_init, function_viz, "Uses if granularity=function")
    Rel(analyzer_init, line_viz, "Uses if granularity=line")
```

## Technical Design

### System Requirements
- Python 3.8+
- Linear.app API access
- GitHub API access
- Sufficient storage for analysis output
- Scikit-learn for predictive modeling
- Pandas for data analysis
- AST parser for code analysis

### Data Flow
1. Linear.app API → Bug tickets with branch names
2. GitHub API → Pull request data for each branch
3. Local processing → File change analysis
4. Output generation → CSV and visualization files
5. Model training → Predictive analysis for new PRs

### Multi-level Granularity Analysis
The system supports heatmap generation at multiple levels of code granularity:

1. **Module Level**
   - Aggregates bugs by module/directory
   - Identifies bug-prone modules
   - Supports custom module grouping
   - Visualization: Tree map with color intensity

2. **File Level**
   - Default analysis level
   - Maps bugs to specific files
   - Tracks file evolution over time
   - Visualization: Bar chart or heatmap matrix

3. **Function/Class Level**
   - Parses source code to identify functions and classes
   - Maps bugs to specific functions
   - Tracks complexity metrics per function
   - Visualization: Nested heatmap with drill-down

4. **Line Level**
   - Utilizes git blame data for precise bug locations
   - Tracks line-specific bug history
   - Identifies problematic code patterns
   - Visualization: Code view with highlighted areas

### Granularity Configuration
```json
{
  "analysis_level": "function",  // Options: "module", "file", "function", "line"
  "grouping": {
    "enabled": true,
    "custom_groups": {
      "frontend": ["src/ui/*", "src/components/*"],
      "backend": ["src/api/*", "src/database/*"]
    }
  },
  "min_bug_threshold": 2,
  "parser_settings": {
    "parse_comments": true,
    "track_line_history": true
  }
}
```

### Predictive Analysis
The system uses historical data to predict the likelihood of bugs in new pull requests by analyzing:

1. **File-based Features**
   - Historical bug frequency per file
   - File complexity metrics
   - File change frequency
   - File ownership patterns

2. **PR-based Features**
   - Number of files changed
   - Lines of code changed
   - Time of day/week
   - Author's historical bug rate
   - Review patterns

3. **Code-based Features**
   - Code complexity metrics
   - Test coverage
   - Dependency changes
   - Code review comments

4. **Model Output**
   - Confidence score (0-100%)
   - Risk factors identified
   - Recommended actions
   - Historical comparisons

### Error Handling
- API rate limiting
- Network connectivity issues
- Missing or invalid data
- File system permissions
- Model training failures

### Performance Considerations
- Batch processing of tickets
- Caching of API responses
- Memory management for large datasets
- Parallel processing capabilities

### Security
- API key management
- Data privacy
- Output file permissions
- Network security

### Monitoring and Logging
- API call tracking
- Error logging
- Performance metrics
- Analysis progress

### Testing Strategy
- Unit tests for each component
- Integration tests for API interactions
- End-to-end testing
- Performance testing

### Deployment
- Environment setup
- Dependency management
- Configuration management
- Update procedures

### Maintenance
- Regular updates
- Bug fixes
- Performance optimization
- Documentation updates

## Features

- Fetches bug tickets from Linear.app
- Associates tickets with GitHub pull requests
- Analyzes files changed in pull requests
- Generates a heatmap showing which files are most prone to bugs
- Supports multi-level granularity analysis (module, file, function, line)
- Provides predictive bug confidence scoring for new PRs

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
LINEAR_API_KEY=your_linear_api_key
GITHUB_TOKEN=your_github_token
```

3. Run the analysis:
```bash
python main.py
```

## Configuration

- Update `config.py` to customize:
  - Linear team ID
  - GitHub repository details
  - Analysis parameters

## Output

The analysis generates:
- A CSV file with bug ticket and PR associations
- A heatmap visualization of bug-prone files
- Summary statistics of bug distribution

## System Components

1. **Linear Client** (`linear_client.py`)
   - Handles communication with Linear.app's GraphQL API
   - Fetches bug tickets and associated metadata

2. **GitHub Client** (`github_client.py`)
   - Manages interaction with GitHub's REST API
   - Retrieves pull request data and file changes
   - Extracts git blame information for line-level analysis

3. **Code Parser** (`code_parser.py`)
   - Parses source code to identify functions and classes
   - Calculates complexity metrics
   - Tracks code structure changes
   - Maps line changes to semantic units

4. **Bug Analyzer** (`analyzer.py`)
   - Processes and correlates data from both systems
   - Generates visualizations and analysis reports
   - Supports different granularity levels
   - Creates interactive drill-down visualizations

5. **Predictive Model** (`predictive_model.py`)
   - Trains on historical bug data
   - Generates confidence scores for new PRs
   - Identifies risk factors
   - Provides recommendations

6. **Main Application** (`main.py`)
   - Orchestrates the entire analysis process
   - Coordinates between different components
   - Manages granularity configuration

## Usage Examples

### Analyzing at Different Granularity Levels

```bash
# Default file-level analysis
python main.py

# Module-level analysis
python main.py --granularity module

# Function-level analysis
python main.py --granularity function

# Line-level analysis
python main.py --granularity line
```

### Custom Grouping

```bash
# Custom module grouping
python main.py --config custom_groups.json
```

### Interactive Exploration

```bash
# Start interactive dashboard
python main.py --interactive
```

## Future Enhancements
- Support for multiple repositories
- Advanced filtering options
- Custom visualization types
- Automated reporting
- Integration with CI/CD pipelines
- Real-time PR risk assessment
- Automated code review suggestions
- Team performance metrics
- Bug prediction accuracy improvements
- IDE integration for inline bug probability visualization

## Troubleshooting
- Common issues and solutions
- Debugging procedures
- Support contact information

## Contributing
- Code style guidelines
- Pull request process
- Testing requirements
- Documentation standards