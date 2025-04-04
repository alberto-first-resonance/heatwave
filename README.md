# Bug Heatmap Analyzer

This project analyzes bug tickets from Linear.app and correlates them with GitHub pull requests to generate a heatmap of bug-prone files.

## System Architecture

```mermaid
C4Context
    title System Context Diagram for Bug Heatmap Analyzer

    Person(developer, "Developer", "Uses the tool to analyze bug patterns")
    System(bug_analyzer, "Bug Heatmap Analyzer", "Python application that analyzes bug patterns")
    System(linear, "Linear.app", "Issue tracking system")
    System(github, "GitHub", "Version control and pull request system")
    System(output, "Output Files", "CSV and visualization files")

    Rel(developer, bug_analyzer, "Runs")
    Rel(bug_analyzer, linear, "Fetches bug tickets via GraphQL API")
    Rel(bug_analyzer, github, "Fetches PR data via REST API")
    Rel(bug_analyzer, output, "Generates")
```

```mermaid
C4Container
    title Container Diagram for Bug Heatmap Analyzer

    Container(bug_analyzer, "Bug Heatmap Analyzer", "Python application")
    ContainerDb(linear_api, "Linear.app API", "GraphQL API")
    ContainerDb(github_api, "GitHub API", "REST API")
    ContainerDb(output_files, "Output Files", "CSV and PNG files")

    Rel(bug_analyzer, linear_api, "Fetches bug tickets")
    Rel(bug_analyzer, github_api, "Fetches PR data")
    Rel(bug_analyzer, output_files, "Generates analysis")
```

## Features

- Fetches bug tickets from Linear.app
- Associates tickets with GitHub pull requests
- Analyzes files changed in pull requests
- Generates a heatmap showing which files are most prone to bugs

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

3. **Bug Analyzer** (`analyzer.py`)
   - Processes and correlates data from both systems
   - Generates visualizations and analysis reports

4. **Main Application** (`main.py`)
   - Orchestrates the entire analysis process
   - Coordinates between different components