"""Command-line interface for GitHub PR files exporter."""

import argparse
from .exporter import process_prs


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(description='Export files changed in GitHub PRs')
    parser.add_argument('--input', required=True, help='Input CSV file with PR numbers')
    parser.add_argument('--output', required=True, help='Output CSV file for results')
    parser.add_argument('--owner', required=True, help='GitHub repository owner')
    parser.add_argument('--repo', required=True, help='GitHub repository name')
    parser.add_argument('--token', required=True, help='GitHub personal access token')
    
    args = parser.parse_args()
    
    process_prs(args.input, args.output, args.owner, args.repo, args.token)


if __name__ == '__main__':
    main() 