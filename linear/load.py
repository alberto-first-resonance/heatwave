import json
from data import issues
import csv

bug_issues_with_github = []
for issue in issues:
    if "issue-type.bug" in {label["name"] for label in issue.get("labels", {}).get("nodes", [])}:
        for edge in issue.get("attachments", {}).get("edges", []):
            node = edge.get("node", {})
            if node.get("sourceType") == "github":
                bug_issues_with_github.append(node.get("url"))


bug_issues_with_github = [b for b in bug_issues_with_github if 'diplo' in b]
pr_numbers = []
for b in bug_issues_with_github:
    pr_numbers.append(b.split('pull/')[-1])
print(pr_numbers)

with open("issues.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["pr_number"])
    for p in pr_numbers:
        writer.writerow([p])

