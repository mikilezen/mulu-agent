"""Transparent editorial checks for Amharic and Afaan Oromo AI copy."""

from __future__ import annotations

import re
from typing import Any

LANGUAGE_NAMES = {"am": "Amharic", "om": "Afaan Oromo", "unknown": "Unknown / mixed"}


def detect_language(text: str, requested: str = "auto") -> str:
    if requested in {"am", "om"}:
        return requested
    if re.search(r"[\u1200-\u137f]", text):
        return "am"
    lowered = text.lower()
    signals = ("akkam", "galatoomi", "tajaajila", "keessaa", "jiru", "dha", "fi")
    return "om" if sum(lowered.count(signal) for signal in signals) >= 2 else "unknown"


def _issue(title: str, message: str, suggestion: str) -> dict[str, str]:
    return {"title": title, "message": message, "suggestion": suggestion}


def review_text(text: str, requested_language: str = "auto") -> dict[str, Any]:
    """Return explainable quality signals without sending text to an external service."""
    stripped = text.strip()
    if not stripped:
        raise ValueError("Text must not be empty.")
    if len(stripped) > 100_000:
        raise ValueError("Text is limited to 100 KB.")

    language = detect_language(stripped, requested_language)
    issues: list[dict[str, str]] = []
    if re.search(r"\s{2,}", stripped):
        issues.append(_issue("Repeated spaces", "Multiple spaces can make generated copy look unfinished.", "Use one space between words."))
    if re.search(r"[!?。，！？]{2,}", stripped):
        issues.append(_issue("Repeated punctuation", "Repeated punctuation is often an AI or informal-chat artifact.", "Keep one sentence-ending mark unless emphasis is intentional."))
    if not re.search(r"[.!?።፣፤፥፦፧፨]$", stripped):
        issues.append(_issue("Missing sentence punctuation", "The text ends without a clear sentence boundary.", "Add the punctuation appropriate to the final sentence."))
    if language == "om":
        lowered = stripped.lower()
        if re.search(r"\b(and|the|of|to)\b", lowered):
            issues.append(_issue("Possible English leakage", "English function words appear in Afaan Oromo copy.", "Confirm whether these words should be translated for the target audience."))
        if re.search(r"\b(akkam|galatoomi)\b.*\b(akkam|galatoomi)\b", lowered):
            issues.append(_issue("Repeated phrase", "A greeting or thanks phrase appears more than once.", "Remove the duplicate unless the repetition is deliberate."))
    if language == "unknown":
        issues.append(_issue("Language not confidently detected", "The text does not contain enough recognizable Amharic or Afaan Oromo signals.", "Choose the language manually and ask a fluent reviewer to confirm it."))

    return {
        "language": language,
        "language_name": LANGUAGE_NAMES[language],
        "score": max(0, 100 - len(issues) * 12),
        "word_count": len(re.findall(r"\S+", stripped)),
        "character_count": len(stripped),
        "summary": "The text is clean on the automatic checks." if not issues else f"{len(issues)} suggestion(s) found. Prioritize meaning and terminology review with a fluent speaker.",
        "issues": issues,
    }
