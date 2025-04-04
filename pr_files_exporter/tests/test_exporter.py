"""Unit tests for the PR Files Exporter module."""

import unittest
from unittest.mock import patch, MagicMock
import csv
import tempfile
import os
from datetime import datetime, timezone
from io import StringIO
from pr_files_exporter.exporter import get_pr_files_graphql, process_prs


class TestPrFilesExporter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.owner = "test-owner"
        self.repo = "test-repo"
        self.github_token = "test-token"
        
        # Create temp files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.input_csv_path = os.path.join(self.temp_dir.name, "input.csv")
        self.output_csv_path = os.path.join(self.temp_dir.name, "output.csv")
        
        # Create test input.csv
        with open(self.input_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["123"])
            writer.writerow(["456"])
            writer.writerow(["789"])
        
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
        
    @patch('requests.post')
    def test_get_pr_files_graphql_single_page(self, mock_post):
        """Test fetching PR files with a single page of results"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
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
        
        mock_post.return_value = mock_response
        
        # Call the function
        pr_files, file_dates = get_pr_files_graphql(self.owner, self.repo, ["123"], self.github_token)
        
        # Assertions
        self.assertEqual(len(pr_files), 1)
        self.assertEqual(pr_files["123"], {"file1.py", "file2.js"})
        
        # Verify file dates
        expected_date = "2023-01-01T12:00:00+00:00"
        self.assertEqual(file_dates["file1.py"], expected_date)
        self.assertEqual(file_dates["file2.js"], expected_date)
        
        # Verify API calls
        self.assertEqual(mock_post.call_count, 1)
    
    @patch('requests.post')
    def test_get_pr_files_graphql_with_pagination(self, mock_post):
        """Test fetching PR files with pagination"""
        # First response with page 1
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {
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
        
        # Second response with page 2
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {
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
        
        mock_post.side_effect = [mock_response1, mock_response2]
        
        # Call the function
        pr_files, file_dates = get_pr_files_graphql(self.owner, self.repo, ["123"], self.github_token)
        
        # Assertions
        self.assertEqual(len(pr_files), 1)
        self.assertEqual(pr_files["123"], {"file1.py", "file2.js"})
        
        # Verify API calls
        self.assertEqual(mock_post.call_count, 2)
    
    @patch('requests.post')
    def test_get_pr_files_graphql_multiple_prs(self, mock_post):
        """Test fetching files from multiple PRs"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
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
        
        mock_post.return_value = mock_response
        
        # Call the function
        pr_files, file_dates = get_pr_files_graphql(self.owner, self.repo, ["123", "456"], self.github_token)
        
        # Assertions
        self.assertEqual(len(pr_files), 2)
        self.assertEqual(pr_files["123"], {"file1.py"})
        self.assertEqual(pr_files["456"], {"file1.py", "file3.css"})
        
        # Verify file dates (should have most recent date)
        expected_date1 = "2023-01-02T12:00:00+00:00"  # Latest date for file1.py
        expected_date3 = "2023-01-02T12:00:00+00:00"  # Date for file3.css
        self.assertEqual(file_dates["file1.py"], expected_date1)
        self.assertEqual(file_dates["file3.css"], expected_date3)
    
    @patch('requests.post')
    def test_get_pr_files_graphql_unmerged_pr(self, mock_post):
        """Test handling of unmerged PRs"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "repository": {
                    "pr0": {
                        "merged": False,
                        "mergedAt": None,
                        "files": {
                            "nodes": [],
                            "pageInfo": {
                                "hasNextPage": False,
                                "endCursor": None
                            }
                        }
                    }
                }
            }
        }
        
        mock_post.return_value = mock_response
        
        # Call the function
        pr_files, file_dates = get_pr_files_graphql(self.owner, self.repo, ["123"], self.github_token)
        
        # Assertions
        self.assertEqual(len(pr_files), 1)
        self.assertEqual(pr_files["123"], set())  # Empty set for unmerged PR
        self.assertEqual(len(file_dates), 0)      # No dates for unmerged PR
    
    @patch('requests.post')
    def test_get_pr_files_graphql_error_handling(self, mock_post):
        """Test error handling in GraphQL response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [{"message": "API rate limit exceeded"}]
        }
        
        mock_post.return_value = mock_response
        
        # Call the function with expected exception
        with self.assertRaises(Exception) as context:
            get_pr_files_graphql(self.owner, self.repo, ["123"], self.github_token)
        
        self.assertTrue("GraphQL errors" in str(context.exception))
    
    @patch('pr_files_exporter.exporter.get_pr_files_graphql')
    def test_process_prs(self, mock_get_files):
        """Test the process_prs function"""
        # Mock return value for get_pr_files_graphql
        mock_get_files.return_value = (
            {
                "123": {"file1.py", "file2.js"},
                "456": {"file2.js", "file3.css"},
                "789": set()  # Unmerged PR
            },
            {
                "file1.py": "2023-01-01T12:00:00+00:00",
                "file2.js": "2023-01-02T12:00:00+00:00",
                "file3.css": "2023-01-02T12:00:00+00:00"
            }
        )
        
        # Run the process_prs function
        process_prs(self.input_csv_path, self.output_csv_path, self.owner, self.repo, self.github_token)
        
        # Verify output CSV
        with open(self.output_csv_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        # Sort rows by filename for consistent test results
        rows.sort(key=lambda x: x[0])
        
        # Check headers and content
        self.assertEqual(headers, ['filename', 'count', 'last_modified'])
        self.assertEqual(len(rows), 3)
        
        # file1.py appears in 1 PR
        self.assertEqual(rows[0][0], 'file1.py')
        self.assertEqual(rows[0][1], '1')
        self.assertEqual(rows[0][2], '2023-01-01T12:00:00+00:00')
        
        # file2.js appears in 2 PRs
        self.assertEqual(rows[1][0], 'file2.js')
        self.assertEqual(rows[1][1], '2')
        self.assertEqual(rows[1][2], '2023-01-02T12:00:00+00:00')
        
        # file3.css appears in 1 PR
        self.assertEqual(rows[2][0], 'file3.css')
        self.assertEqual(rows[2][1], '1')
        self.assertEqual(rows[2][2], '2023-01-02T12:00:00+00:00')
    
    @patch('pr_files_exporter.exporter.get_pr_files_graphql')
    def test_process_prs_error_handling(self, mock_get_files):
        """Test error handling in process_prs"""
        # Set up mock to raise an exception
        mock_get_files.side_effect = Exception("Test error")
        
        # Run process_prs with expected exception
        with patch('builtins.print') as mock_print:
            process_prs(self.input_csv_path, self.output_csv_path, self.owner, self.repo, self.github_token)
            
            # Verify error was logged
            mock_print.assert_any_call("Error processing PRs: Test error")


if __name__ == '__main__':
    unittest.main() 