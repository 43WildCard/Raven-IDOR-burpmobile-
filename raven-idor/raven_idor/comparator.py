from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

from .parser import HTTPResponse

SECRET_HEADER_NAMES = {
    "authorization", "proxy-authorization", "cookie", "set-cookie",
    "x-api-key", "x-auth-token",
}

SECRET_BODY_KEYS = re.compile(
    r'(?i)\b(password|passwd|secret|token|api[_-]?key|authorization|cookie|session)\b'
)


@dataclass
class Comparison:
    status_a: int
    status_b: int
    content_length_a: int
    content_length_b: int
    body_similarity: float
    changed_headers: list[str]
    suspicious_observations: list[str]
    assessment: str


def _safe_body(body: str) -> str:
    # Avoid making a secret appear in comparison output.
    return SECRET_BODY_KEYS.sub("<SENSITIVE_KEY>", body)


def compare_responses(a: HTTPResponse, b: HTTPResponse) -> Comparison:
    body_a = _safe_body(a.body)
    body_b = _safe_body(b.body)

    ratio = difflib.SequenceMatcher(None, body_a, body_b).ratio() * 100.0

    changed = []
    all_names = {k.lower() for k in a.headers} | {k.lower() for k in b.headers}
    for name in sorted(all_names):
        if name in SECRET_HEADER_NAMES:
            continue
        va = next((v for k, v in a.headers.items() if k.lower() == name), None)
        vb = next((v for k, v in b.headers.items() if k.lower() == name), None)
        if va != vb:
            changed.append(name)

    observations = []
    if a.status_code != b.status_code:
        observations.append("HTTP status differs")
    if abs(len(body_a) - len(body_b)) > 0:
        observations.append("response body length differs")
    if ratio < 95:
        observations.append("response bodies contain meaningful differences")

    # This is deliberately conservative: differences are never called an IDOR.
    assessment = "MANUAL REVIEW REQUIRED" if observations else "NO MATERIAL DIFFERENCE DETECTED"

    return Comparison(
        a.status_code, b.status_code,
        len(a.body.encode("utf-8")), len(b.body.encode("utf-8")),
        ratio, changed, observations, assessment
    )
