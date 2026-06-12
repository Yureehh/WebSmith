import argparse
import json
import sys
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings


def response_text(payload: dict[str, Any]) -> str:
    text = payload.get("output_text") or ""
    if text:
        return text
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            text += content.get("text") or ""
    return text


def post_response(client: httpx.Client, body: dict[str, Any]) -> dict[str, Any]:
    response = client.post(
        f"{settings.openai_base_url.rstrip('/')}/responses",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        json=body,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual OpenAI smoke check for WebSmith.")
    parser.add_argument(
        "--web-search",
        action="store_true",
        help="Also run one Responses API web-search call. This may incur tool-call cost.",
    )
    args = parser.parse_args()

    if not settings.openai_api_key:
        raise SystemExit(
            "OPENAI_API_KEY is missing. Add it to .env before running this smoke test."
        )

    with httpx.Client(timeout=40) as client:
        structured_payload = post_response(
            client,
            {
                "model": settings.openai_model,
                "input": (
                    "Return only JSON with keys ok, task, and note. "
                    'Use: {"ok": true, "task": "structured_smoke", "note": "..."}'
                ),
            },
        )
        parsed = json.loads(response_text(structured_payload))
        if parsed.get("ok") is not True or parsed.get("task") != "structured_smoke":
            raise SystemExit(f"Unexpected structured response: {parsed}")
        print(f"Structured response OK with {settings.openai_model}")

        if args.web_search:
            web_payload = post_response(
                client,
                {
                    "model": settings.openai_model,
                    "tools": [{"type": "web_search"}],
                    "tool_choice": "auto",
                    "include": ["web_search_call.action.sources"],
                    "input": (
                        "Find the official website for Comune di Forli. "
                        "Return one sentence with citation."
                    ),
                },
            )
            if not response_text(web_payload):
                raise SystemExit("Web-search response did not include output text.")
            print("Web-search response OK")


if __name__ == "__main__":
    main()
