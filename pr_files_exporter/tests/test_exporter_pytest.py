"""Pytest-based tests for the PR Files Exporter module."""

import pytest
from unittest.mock import patch, MagicMock
import csv
import tempfile
import os
from datetime import datetime, timezone
from io import StringIO
from pr_files_exporter.exporter import get_pr_files_graphql, process_prs


@pytest.fixture
def temp_files():
    """Create temporary input and output files for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_csv_path = os.path.join(temp_dir, "input.csv")
        output_csv_path = os.path.join(temp_dir, "output.csv")
        
        # Create test input.csv
        with open(input_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["123"])
            writer.writerow(["456"])
        
        yield input_csv_path, output_csv_path


@pytest.fixture
def github_params():
    """Return GitHub API parameters for testing"""
    return {
        "owner": "test-owner",
        "repo": "test-repo",
        "token": "test-token"
    }


@pytest.fixture
def mock_graphql_response():
    """Create a mock GraphQL response with merged PR data"""
    response = MagicMock()
    response.json.return_value = {
        "data": {
            "repository": {
                "pr0": {
                    "merged": True,
                    "mergedAt": "2023-01-01T12:00:00Z",
                    "files": {
                        "nodes": [
                            {"path": "file1.py"},
                            {"path": "file2.js"}
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None
                        }
                    }
                }
            }
        }
    }
    return response


@pytest.fixture
def mock_graphql_paginated_response():
    """Create mock responses for paginated GraphQL results"""
    response1 = MagicMock()
    response1.json.return_value = {
        "data": {
            "repository": {
                "pr0": {
                    "merged": True,
                    "mergedAt": "2023-01-01T12:00:00Z",
                    "files": {
                        "nodes": [
                            {"path": "file1.py"}
                        ],
                        "pageInfo": {
                            "hasNextPage": True,
                            "endCursor": "cursor1"
                        }
                    }
                }
            }
        }
    }
    
    response2 = MagicMock()
    response2.json.return_value = {
        "data": {
            "repository": {
                "pullRequest": {
                    "files": {
                        "nodes": [
                            {"path": "file2.js"}
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None
                        }
                    }
                }
            }
        }
    }
    
    return [response1, response2]


@pytest.fixture
def mock_graphql_multiple_prs_response():
    """Create a mock response with data for multiple PRs"""
    response = MagicMock()
    response.json.return_value = {
        "data": {
            "repository": {
                "pr0": {
                    "merged": True,
                    "mergedAt": "2023-01-01T12:00:00Z",
                    "files": {
                        "nodes": [
                            {"path": "file1.py"}
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None
                        }
                    }
                },
                "pr1": {
                    "merged": True,
                    "mergedAt": "2023-01-02T12:00:00Z",
                    "files": {
                        "nodes": [
                            {"path": "file1.py"},
                            {"path": "file3.css"}
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None
                        }
                    }
                }
            }
        }
    }
    return response


def test_get_pr_files_graphql_single_page(github_params, mock_graphql_response):
    """Test fetching PR files with a single page of results"""
    with patch('requests.post', return_value=mock_graphql_response):
        pr_files, file_dates = get_pr_files_graphql(
            github_params["owner"], 
            github_params["repo"], 
            ["123"], 
            github_params["token"]
        )
        
        # Assertions
        assert len(pr_files) == 1
        assert pr_files["123"] == {"file1.py", "file2.js"}
        
        # Verify file dates
        expected_date = "2023-01-01T12:00:00+00:00"
        assert file_dates["file1.py"] == expected_date
        assert file_dates["file2.js"] == expected_date


def test_get_pr_files_graphql_with_pagination(github_params, mock_graphql_paginated_response):
    """Test fetching PR files with pagination"""
    with patch('requests.post', side_effect=mock_graphql_paginated_response):
        pr_files, file_dates = get_pr_files_graphql(
            github_params["owner"], 
            github_params["repo"], 
            ["123"], 
            github_params["token"]
        )
        
        # Assertions
        assert len(pr_files) == 1
        assert pr_files["123"] == {"file1.py", "file2.js"}
        
        # Verify file dates
        expected_date = "2023-01-01T12:00:00+00:00"
        assert file_dates["file1.py"] == expected_date
        assert file_dates["file2.js"] == expected_date


def test_get_pr_files_graphql_multiple_prs(github_params, mock_graphql_multiple_prs_response):
    """Test fetching files from multiple PRs"""
    with patch('requests.post', return_value=mock_graphql_multiple_prs_response):
        pr_files, file_dates = get_pr_files_graphql(
            github_params["owner"], 
            github_params["repo"], 
            ["123", "456"], 
            github_params["token"]
        )
        
        # Assertions
        assert len(pr_files) == 2
        assert pr_files["123"] == {"file1.py"}
        assert pr_files["456"] == {"file1.py", "file3.css"}
        
        # Verify file dates (should have most recent date)
        expected_date1 = "2023-01-02T12:00:00+00:00"  # Latest date for file1.py
        expected_date3 = "2023-01-02T12:00:00+00:00"  # Date for file3.css
        assert file_dates["file1.py"] == expected_date1
        assert file_dates["file3.css"] == expected_date3


def test_get_pr_files_graphql_error_handling(github_params):
    """Test error handling in GraphQL response"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "errors": [{"message": "API rate limit exceeded"}]
    }
    
    with patch('requests.post', return_value=mock_response):
        with pytest.raises(Exception) as excinfo:
            get_pr_files_graphql(
                github_params["owner"], 
                github_params["repo"], 
                ["123"], 
                github_params["token"]
            )
        
        assert "GraphQL errors" in str(excinfo.value)


def test_process_prs(temp_files, github_params):
    """Test the process_prs function"""
    input_csv_path, output_csv_path = temp_files
    
    # Mock return value for get_pr_files_graphql
    mock_return_value = (
        {
            "123": {"file1.py", "file2.js"},
            "456": {"file2.js", "file3.css"}
        },
        {
            "file1.py": "2023-01-01T12:00:00+00:00",
            "file2.js": "2023-01-02T12:00:00+00:00",
            "file3.css": "2023-01-02T12:00:00+00:00"
        }
    )
    
    with patch('pr_files_exporter.exporter.get_pr_files_graphql', return_value=mock_return_value):
        # Capture print statements
        with patch('builtins.print'):
            process_prs(
                input_csv_path, 
                output_csv_path, 
                github_params["owner"], 
                github_params["repo"], 
                github_params["token"]
            )
        
        # Verify output CSV
        with open(output_csv_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        # Sort rows by filename for consistent test results
        rows.sort(key=lambda x: x[0])
        
        # Check headers and content
        assert headers == ['filename', 'count', 'last_modified']
        assert len(rows) == 3
        
        # file1.py appears in 1 PR
        assert rows[0][0] == 'file1.py'
        assert rows[0][1] == '1'
        assert rows[0][2] == '2023-01-01T12:00:00+00:00'
        
        # file2.js appears in 2 PRs
        assert rows[1][0] == 'file2.js'
        assert rows[1][1] == '2'
        assert rows[1][2] == '2023-01-02T12:00:00+00:00'
        
        # file3.css appears in 1 PR
        assert rows[2][0] == 'file3.css'
        assert rows[2][1] == '1'
        assert rows[2][2] == '2023-01-02T12:00:00+00:00'


def test_process_prs_error_handling(temp_files, github_params):
    """Test error handling in process_prs"""
    input_csv_path, output_csv_path = temp_files
    
    with patch('pr_files_exporter.exporter.get_pr_files_graphql', side_effect=Exception("Test error")):
        # Capture print statements
        with patch('builtins.print') as mock_print:
            process_prs(
                input_csv_path, 
                output_csv_path, 
                github_params["owner"], 
                github_params["repo"], 
                github_params["token"]
            )
            
            # Verify error was logged
            mock_print.assert_any_call("Error processing PRs: Test error") 