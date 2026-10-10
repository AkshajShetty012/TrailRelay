
import json

import httpx
from temporalio import activity


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
