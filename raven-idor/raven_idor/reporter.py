from __future__ import annotations

import json
import re
from pathlib import Path

from .identifiers import candidates_from_request
from .parser import parse_request

SENSITIVE_NAME_RE = re.compile(
    r"(?i)(cookie|authorization|token|password|passwd|secret|api[_-]?key|session)"
)


def redact_value(name: str, value: str) -> str:
    if SENSITIVE_NAME_RE.search(name):
        return "[REDACTED]"
    return value


def report_data(request):
    candidates = candidates_from_request(request)
    return {
        "method": request.method,
        "endpoint": request.path + (("?" + request.query) if request.query else ""),
        "parameters": [
            {
                "name": c.name,
                "value": redact_value(c.name, c.value),
                "type": c.location,
                "value_type": c.value_type,
                "confidence": c.confidence,
                "reasons": c.reasons,
            }
            for c in candidates
        ],
    }


def markdown_report(request):
    data = report_data(request)
    lines = [
        "# RAVEN IDOR Analyzer Report",
        "",
        "> Offline analysis only. Identifier confidence is a heuristic and does not prove an IDOR.",
        "",
        f"- **Method:** `{data['method']}`",
        f"- **Endpoint:** `{data['endpoint']}`",
        "",
        "## Identifier candidates",
        "",
    ]
    if not data["parameters"]:
        lines.append("No identifier-like candidates were detected.")
    else:
        lines += [
            "| Name | Location | Value type | Confidence | Value |",
            "|---|---|---|---|---|",
        ]
        for p in data["parameters"]:
            lines.append(
                f"| `{p['name']}` | {p['type']} | {p['value_type']} | "
                f"**{p['confidence']}** | `{p['value']}` |"
            )

    lines += [
        "",
        "## Observations",
        "",
        "- Review whether the identified object is authorization-sensitive.",
        "- Compare behavior using two requests that were obtained lawfully and are within scope.",
        "- A response difference alone is not evidence of an IDOR.",
        "",
        "## Manual verification checklist",
        "",
        "- [ ] Confirm the target is explicitly in scope.",
        "- [ ] Confirm both requests were obtained using authorized accounts/sessions.",
        "- [ ] Confirm no brute force or mass enumeration is used.",
        "- [ ] Compare only the minimum data needed to establish authorization behavior.",
        "- [ ] Verify that a different object cannot be accessed by an unauthorized principal.",
        "- [ ] Record reproducible evidence without exposing cookies, tokens, passwords, or API keys.",
        "",
    ]
    return "\n".join(lines)


def write_report(request_path, output_path):
    request = parse_request(Path(request_path).read_text(encoding="utf-8", errors="replace"))
    Path(output_path).write_text(markdown_report(request), encoding="utf-8")
