import csv
import requests
from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple
import argparse
from datetime import datetime, timezone

def get_pr_files_graphql(owner: str, repo: str, pr_numbers: List[str], github_token: str) -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    """Fetch all files changed in multiple pull requests using GraphQL with pagination."""
    pr_files = {pr_number: set() for pr_number in pr_numbers}
    # Use timezone-aware datetime.min
    file_dates = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))
    
    # Process PRs in batches of 10 to avoid query complexity limits
    batch_size = 10
    for i in range(0, len(pr_numbers), batch_size):
        batch = pr_numbers[i:i + batch_size]
        
        # Construct the GraphQL query for this batch
        pr_fragments = []
        for j, pr_number in enumerate(batch):
            pr_fragments.append(f"""
            pr{j}: pullRequest(number: {pr_number}) {{
                merged
                mergedAt
                files(first: 100) {{
                    nodes {{
                        path
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
            """)

        query = f"""
        query {{
            repository(owner: "{owner}", name: "{repo}") {{
                {"".join(pr_fragments)}
            }}
        }}
        """

        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json"
        }

        # Process each PR in the batch
        for j, pr_number in enumerate(batch):
            cursor = None
            
            # Initial query to check if PR is merged
            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": query},
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            pr_data = data["data"]["repository"][f"pr{j}"]
            
            # Skip if PR is not merged
            if not pr_data["merged"]:
                print(f"Skipping PR #{pr_number} as it is not merged")
                continue
            
            # Get the merge date
            merged_at = pr_data["mergedAt"]
            if merged_at:
                # Parse the ISO format date and ensure it's timezone-aware
                merge_date = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            else:
                continue  # Skip if no merge date (shouldn't happen for merged PRs)
                
            # Process first page of files
            files_data = pr_data["files"]
            file_paths = [file["path"] for file in files_data["nodes"]]
            pr_files[pr_number].update(file_paths)
            
            # Update file dates
            for file_path in file_paths:
                if merge_date > file_dates[file_path]:
                    file_dates[file_path] = merge_date
            
            # Check if we need to fetch more files
            page_info = files_data["pageInfo"]
            if not page_info["hasNextPage"]:
                continue
                
            cursor = page_info["endCursor"]
            
            # Fetch additional pages if needed
            while cursor:
                pagination_query = f"""
                query {{
                    repository(owner: "{owner}", name: "{repo}") {{
                        pullRequest(number: {pr_number}) {{
                            files(first: 100, after: "{cursor}") {{
                                nodes {{
                                    path
                                }}
                                pageInfo {{
                                    hasNextPage
                                    endCursor
                                }}
                            }}
                        }}
                    }}
                }}
                """
                
                response = requests.post(
                    "https://api.github.com/graphql",
                    json={"query": pagination_query},
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                if "errors" in data:
                    raise Exception(f"GraphQL errors: {data['errors']}")
                
                pagination_data = data["data"]["repository"]["pullRequest"]["files"]
                file_paths = [file["path"] for file in pagination_data["nodes"]]
                pr_files[pr_number].update(file_paths)
                
                # Update file dates
                for file_path in file_paths:
                    if merge_date > file_dates[file_path]:
                        file_dates[file_path] = merge_date
                
                if not pagination_data["pageInfo"]["hasNextPage"]:
                    break
                    
                cursor = pagination_data["pageInfo"]["endCursor"]
    
    # Convert datetime objects to ISO format strings
    formatted_dates = {file_path: date.isoformat() for file_path, date in file_dates.items() if date > datetime.min.replace(tzinfo=timezone.utc)}
    
    return pr_files, formatted_dates

def process_prs(input_csv: str, output_csv: str, owner: str, repo: str, github_token: str):
    """Process PRs from input CSV and generate file frequency output CSV."""
    file_counter = Counter()
    
    # Read PR numbers from input CSV
    with open(input_csv, 'r') as f:
        reader = csv.reader(f)
        pr_numbers = [row[0] for row in reader]
    
    print(f"Processing {len(pr_numbers)} PRs from {input_csv}")
    
    try:
        # Get all PR files in batches with pagination
        pr_files, file_dates = get_pr_files_graphql(owner, repo, pr_numbers, github_token)
        
        # Count file occurrences (only for merged PRs)
        merged_count = 0
        for pr_number, files in pr_files.items():
            if files:  # If there are files, the PR was merged
                file_counter.update(files)
                merged_count += 1
        
        print(f"Found {merged_count} merged PRs out of {len(pr_numbers)} total PRs")
            
    except Exception as e:
        print(f"Error processing PRs: {str(e)}")
        return
    
    # Write results to output CSV
    total_files = sum(1 for _ in file_counter.keys())
    print(f"Writing {total_files} unique files to {output_csv}")
    
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'count', 'last_modified'])
        for filename, count in file_counter.most_common():
            last_modified = file_dates.get(filename, "")  # Use empty string if no date found
            writer.writerow([filename, count, last_modified])
    
    print(f"Done! Output written to {output_csv}")

def main():
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