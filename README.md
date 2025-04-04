# GitHub PR Files Exporter

This script analyzes GitHub pull requests and generates a report of file changes across multiple PRs.

## Requirements

- Python 3.6+
- GitHub Personal Access Token with `repo` scope

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Create an input CSV file with one column containing PR numbers
2. Run the script with the following arguments:
```bash
python pr_files_exporter.py \
    --input input.csv \
    --output output.csv \
    --owner owner \
    --repo repo \
    --token token
```

### Arguments

- `--input`: Path to input CSV file containing PR numbers
- `--output`: Path to output CSV file
- `--owner`: GitHub repository owner/organization
- `--repo`: GitHub repository name
- `--token`: GitHub personal access token

### Output

The script generates a CSV file with two columns:
- `filename`: Name of the file that was changed
- `count`: Number of times the file appeared across all PRs

## Example

Input CSV (`input.csv`):
```
123
456
789
```

Output CSV (`output.csv`):
```
filename,count
src/main.py,3
tests/test_main.py,2
README.md,1
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

The tests use Python's unittest framework with pytest and mock the GitHub API responses to avoid actual API calls during testing. 