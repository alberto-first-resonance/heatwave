"""Unit tests for the PR Files Exporter CLI module."""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pr_files_exporter.cli import main


class TestCli(unittest.TestCase):
    """Test cases for the command-line interface."""
    
    @patch('pr_files_exporter.cli.process_prs')
    def test_main_function(self, mock_process):
        """Test the main function with command line arguments"""
        # Mock command line arguments
        test_args = [
            'pr_files_export.py',
            '--input', 'input.csv',
            '--output', 'output.csv',
            '--owner', 'test-owner',
            '--repo', 'test-repo',
            '--token', 'test-token'
        ]
        
        with patch('sys.argv', test_args):
            main()
            
            # Verify process_prs was called with correct arguments
            mock_process.assert_called_once_with(
                'input.csv', 
                'output.csv',
                'test-owner',
                'test-repo',
                'test-token'
            )


if __name__ == '__main__':
    unittest.main() 