
import json

import httpx
from temporalio import activity
import os


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"

CATEGORIES = {
    "fallen_tree",
    "flooding",
    "washed_out_path",
    "wildlife",
    "damaged_bridge_or_stairs",
    "missing_signage",
    "litter",
    "other",
}


@activity.defn
async def classify_report(note: str) -> dict:
    prompt = f"""
Classify this trail hazard report.

Choose exactly one category from:
fallen_tree, flooding, washed_out_path, wildlife,
damaged_bridge_or_stairs, missing_signage, litter, other.

Return JSON with exactly these fields:
category, description, location_clue.

Use the category values exactly as written.
If uncertain, use other.
Do not invent a location.

Report: {note}
"""

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "format": "json",
                "stream": False,
            },
        )
        response.raise_for_status()

    result = json.loads(response.json()["response"])

    if result.get("category") not in CATEGORIES:
        result["category"] = "other"

    return {
        "category": result["category"],
        "description": str(result.get("description", note)),
        "location_clue": str(result.get("location_clue", "Unknown")),
    }


@activity.defn
async def create_github_issue(report_id: str, report: dict) -> dict:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")

    if not token or not repo:
        raise RuntimeError(
            "GITHUB_TOKEN and GITHUB_REPO must be configured."
        )

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    marker = f"<!-- trailrelay:{report_id} -->"
    base_url = f"https://api.github.com/repos/{repo}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Avoid creating another issue when a workflow activity retries.
        existing = await client.get(
            f"{base_url}/issues",
            headers=headers,
            params={"state": "all", "per_page": 100},
        )
        existing.raise_for_status()

        for issue in existing.json():
            if (
                "pull_request" not in issue
                and marker in (issue.get("body") or "")
            ):
                return {
                    "number": issue["number"],
                    "url": issue["html_url"],
                    "created": False,
                }

        category = report["category"].replace("_", " ").title()
        location = report["location_clue"]

        title = f"[Trail hazard] {category} — {location}"
        body = (
            "## Trail hazard report\n\n"
            f"**Category:** {report['category']}\n\n"
            f"**Description:** {report['description']}\n\n"
            f"**Location clue:** {location}\n\n"
            f"{marker}\n\n"
            "Created automatically by TrailRelay."
        )

        response = await client.post(
            f"{base_url}/issues",
            headers=headers,
            json={"title": title, "body": body},
        )
        response.raise_for_status()
        issue = response.json()

    return {
        "number": issue["number"],
        "url": issue["html_url"],
        "created": True,
    }
