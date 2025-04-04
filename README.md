# GitHub PR Files Exporter

This package analyzes GitHub pull requests and generates a report of file changes across multiple PRs.

## Requirements

- Python 3.6+
- GitHub Personal Access Token with `repo` scope

## Installation

### From Source

1. Clone this repository
2. Install the package:
```bash
pip install -e .
```

### Using pip

```bash
pip install pr_files_exporter
```

## Usage

### Command Line

```bash
python pr_files_export.py \
    --input input.csv \
    --output output.csv \
    --owner owner \
    --repo repo \
    --token token
```

### As a Module

```python
from pr_files_exporter import process_prs

process_prs(
    input_csv='input.csv',
    output_csv='output.csv',
    owner='your-owner',
    repo='your-repo',
    github_token='your-token'
)
```

## Arguments

- `--input`: Path to input CSV file containing PR numbers
- `--output`: Path to output CSV file
- `--owner`: GitHub repository owner/organization
- `--repo`: GitHub repository name
- `--token`: GitHub personal access token

## Output

The script generates a CSV file with three columns:
- `filename`: Name of the file that was changed
- `count`: Number of times the file appeared across all PRs
- `last_modified`: ISO-formatted date when the file was last modified in a merged PR

## Example

Input CSV (`input.csv`):
```
123
456
789
```

Output CSV (`output.csv`):
```
filename,count,last_modified
src/main.py,3,2023-01-15T12:34:56+00:00
tests/test_main.py,2,2023-01-14T10:20:30+00:00
README.md,1,2023-01-10T08:15:00+00:00
```

## Project Structure

```
pr_files_exporter/          # Main package
  ├── __init__.py           # Package initialization
  ├── exporter.py           # Core functionality  
  ├── cli.py                # Command-line interface
  └── tests/                # Test directory
      ├── __init__.py
      ├── test_exporter.py  # Unittest-based tests
      ├── test_cli.py       # CLI tests
      ├── test_exporter_pytest.py  # Pytest-based tests
      └── test_cli_pytest.py       # Pytest-based CLI tests
```

## Testing

To run the unit tests:

```bash
pytest
```

Or to run with verbose output:

```bash
pytest -v
```

The tests use both Python's unittest framework and pytest to mock the GitHub API responses. 