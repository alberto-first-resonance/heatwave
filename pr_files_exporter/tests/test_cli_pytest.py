"""Pytest-based tests for the PR Files Exporter CLI module."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pr_files_exporter.cli import main


@pytest.fixture
def cli_args():
    """Command line arguments for testing"""
    return [
        'pr_files_export.py',
        '--input', 'input.csv',
        '--output', 'output.csv',
        '--owner', 'test-owner',
        '--repo', 'test-repo',
        '--token', 'test-token'
    ]


def test_main_function(cli_args):
    """Test the main function with command line arguments"""
    with patch('pr_files_exporter.cli.process_prs') as mock_process:
        with patch('sys.argv', cli_args):
            main()
            
            # Verify process_prs was called with correct arguments
            mock_process.assert_called_once_with(
                'input.csv', 
                'output.csv',
                'test-owner',
                'test-repo',
                'test-token'
            ) 