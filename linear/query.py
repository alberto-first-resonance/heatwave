import requests
import time
import os
import json
LINEAR_API_URL = "https://api.linear.app/graphql"

QUERY = """
query Issues($after: String) {
  issues(
    first: 150
    after: $after
    filter: {
      createdAt: { gt: "2024-01-01" }
      labels: { some: { name: { eq: "issue-type.bug" } } }
    }
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      id
      labels {
        nodes {
          name
        }
      }
      attachments(filter: { sourceType: { eq: "github" } }) {
        edges {
          node {
            url
            sourceType
          }
        }
      }
    }
  }
}
"""

def fetch_all_issues(api_key):
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    after = None
    all_issues = []

    while True:
        response = requests.post(
            LINEAR_API_URL,
            json={"query": QUERY, "variables": {"after": after}},
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        issues_data = data["data"]["issues"]
        all_issues.extend(issues_data["nodes"])

        if not issues_data["pageInfo"]["hasNextPage"]:
            break

        after = issues_data["pageInfo"]["endCursor"]
        time.sleep(0.5)  # Delay to avoid hitting rate limits

    return all_issues


if __name__ == "__main__":

    issues = fetch_all_issues(os.getenv("API_KEY"))
    print(f"Fetched {len(issues)} issues.")

    f = open("data.json", "w")
    json.dump(issues, f, indent=2)