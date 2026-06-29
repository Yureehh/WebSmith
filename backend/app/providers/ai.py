import json
import logging
from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger("websmith.ai")


def _log_model_failure(model: str, exc: Exception) -> None:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    logger.warning("AI model %s failed%s: %s", model, f" (HTTP {status})" if status else "", exc)


def ai_configured() -> bool:
    return bool(settings.openai_api_key)


def require_ai() -> None:
    if not ai_configured():
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is required for this action.",
        )


def complete_text(system: str, user: str) -> str:
    require_ai()
    errors: list[str] = []
    for model in [settings.openai_model, *settings.openai_backup_models]:
        with httpx.Client(timeout=20) as client:
            try:
                response = client.post(
                    f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        "temperature": 0.4,
                    },
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                return content.strip()
            except Exception as exc:
                _log_model_failure(model, exc)
                errors.append(f"{model}: {exc}")
    raise HTTPException(status_code=502, detail=f"AI provider request failed: {' | '.join(errors)}")


def complete_json(system: str, user: str, required_keys: set[str] | None = None) -> dict[str, Any]:
    text = complete_text(
        system=system,
        user=f"{user}\n\nReturn only valid JSON.",
    )
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            missing = required_keys - set(parsed) if required_keys else set()
            if missing:
                raise HTTPException(
                    status_code=502,
                    detail=f"AI provider returned JSON missing keys: {', '.join(sorted(missing))}.",
                )
            return parsed
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="AI provider returned invalid JSON.") from exc
    raise HTTPException(status_code=502, detail="AI provider returned a non-object JSON value.")


def extract_web_sources(output: list[dict[str, Any]]) -> list[dict[str, str | int | None]]:
    sources: list[dict[str, str | int | None]] = []
    seen_urls: set[str] = set()
    for item in output:
        if item.get("type") == "web_search_call":
            action = item.get("action") or {}
            for source in action.get("sources") or []:
                url = source.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                sources.append(
                    {
                        "url": url,
                        "title": source.get("title"),
                        "source_kind": "web_search_source",
                    }
                )
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            for annotation in content.get("annotations") or []:
                if annotation.get("type") != "url_citation":
                    continue
                url = annotation.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                sources.append(
                    {
                        "url": url,
                        "title": annotation.get("title"),
                        "source_kind": "url_citation",
                        "start_index": annotation.get("start_index"),
                        "end_index": annotation.get("end_index"),
                    }
                )
    return sources


def web_search_json(query: str, required_keys: set[str] | None = None) -> dict[str, Any]:
    require_ai()
    errors: list[str] = []
    for model in [settings.openai_model, *settings.openai_backup_models]:
        with httpx.Client(timeout=35) as client:
            try:
                response = client.post(
                    f"{settings.openai_base_url.rstrip('/')}/responses",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "tools": [{"type": "web_search"}],
                        "tool_choice": "auto",
                        "include": ["web_search_call.action.sources"],
                        "input": query,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                output_text = payload.get("output_text") or ""
                if not output_text:
                    for item in payload.get("output", []):
                        if item.get("type") == "message":
                            for content in item.get("content", []):
                                output_text += content.get("text") or ""
                parsed = json.loads(output_text)
                if isinstance(parsed, dict):
                    missing = required_keys - set(parsed) if required_keys else set()
                    if missing:
                        raise HTTPException(
                            status_code=502,
                            detail=(
                                "AI web search returned JSON missing keys: "
                                f"{', '.join(sorted(missing))}."
                            ),
                        )
                    output = payload.get("output", [])
                    parsed["_raw_sources"] = output
                    parsed["_sources"] = extract_web_sources(output)
                    return parsed
            except Exception as exc:
                _log_model_failure(model, exc)
                errors.append(f"{model}: {exc}")
    raise HTTPException(
        status_code=502,
        detail=f"AI web search request failed: {' | '.join(errors)}",
    )
