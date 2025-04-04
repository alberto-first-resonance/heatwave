"""
GitHub PR Files Exporter module.

This module analyzes GitHub pull requests and generates reports of file changes across multiple PRs.
"""

from .exporter import get_pr_files_graphql, process_prs

__version__ = "0.1.0" 