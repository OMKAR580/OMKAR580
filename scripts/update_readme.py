"""
Auto-updates the 'Currently Building' section in README.md
with the 3 most recently pushed repositories.
"""

import requests
import re
import os
import sys

USERNAME = "OMKAR580"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
README_PATH = "README.md"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

LANG_EMOJI = {
    "Python": "🐍",
    "JavaScript": "⚡",
    "TypeScript": "💙",
    "HTML": "🌐",
    "CSS": "🎨",
    "Java": "☕",
    "C++": "⚙️",
    "C": "🔧",
    "Kotlin": "📱",
    "Rust": "🦀",
    "Go": "🐹",
    "Shell": "💻",
}

def fetch_recent_repos(n=3):
    url = f"https://api.github.com/users/{USERNAME}/repos"
    params = {"sort": "pushed", "per_page": 10, "type": "owner"}
    resp = requests.get(url, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"GitHub API error: {resp.status_code}")
        sys.exit(1)
    repos = resp.json()
    filtered = [r for r in repos if r["name"] != USERNAME and not r["fork"]]
    return filtered[:n]

def build_table(repos):
    header = (
        "| 🚀 Project | 📝 Description | 🛠️ Tech |\n"
        "|:-----------|:---------------|:--------|\n"
    )
    rows = []
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        desc = (repo.get("description") or "Building something awesome...").strip()
        desc = desc[:58] + "..." if len(desc) > 58 else desc
        lang = repo.get("language") or "Code"
        emoji = LANG_EMOJI.get(lang, "🛠️")
        rows.append(f"| [{name}]({url}) | {desc} | {emoji} `{lang}` |")
    return header + "\n".join(rows)

def update_readme(table_content):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    new_section = (
        "<!-- RECENT_REPOS_START -->\n"
        + table_content
        + "\n<!-- RECENT_REPOS_END -->"
    )
    pattern = r"<!-- RECENT_REPOS_START -->.*?<!-- RECENT_REPOS_END -->"
    updated = re.sub(pattern, new_section, content, flags=re.DOTALL)
    if updated == content:
        print("No markers found — skipping.")
        return False
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)
    return True

def main():
    print("Fetching recent repos...")
    repos = fetch_recent_repos(3)
    if not repos:
        print("No repos found.")
        return
    for r in repos:
        print(f"  → {r['name']} ({r.get('language', 'N/A')})")
    table = build_table(repos)
    changed = update_readme(table)
    print("README updated!" if changed else "No changes needed.")

if __name__ == "__main__":
    main()
