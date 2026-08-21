from __future__ import annotations

import re
from dataclasses import dataclass

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)
OBJECTID_RE = re.compile(r"^[0-9a-fA-F]{24}$")
NUMERIC_RE = re.compile(r"^\d{1,20}$")

HIGH_NAMES = {
    "id", "user_id", "userid", "account_id", "profile_id", "order_id",
    "document_id", "file_id", "uid", "object_id", "record_id", "member_id",
    "customer_id", "invoice_id", "message_id", "post_id", "item_id",
}
MEDIUM_NAME_PARTS = (
    "id", "_id", "uuid", "guid", "account", "profile", "user", "object",
    "document", "file", "order", "record", "member", "customer", "invoice",
)


@dataclass
class Candidate:
    name: str
    value: str
    location: str
    value_type: str
    confidence: str
    reasons: list[str]


def classify_value(value: str) -> tuple[str, str, list[str]]:
    value = str(value)
    if UUID_RE.fullmatch(value):
        return "UUID", "HIGH", ["UUID-shaped value"]
    if OBJECTID_RE.fullmatch(value):
        return "object-id", "HIGH", ["MongoDB ObjectId-like value"]
    if NUMERIC_RE.fullmatch(value):
        return "numeric", "MEDIUM", ["numeric identifier-shaped value"]
    return "other", "LOW", []


def classify(name: str, value: str) -> tuple[str, str, list[str]]:
    lname = name.lower().strip()
    vtype, value_conf, reasons = classify_value(value)

    if lname in HIGH_NAMES:
        reasons.append("identifier-like parameter name")
        return vtype, "HIGH", reasons
    if any(part in lname for part in MEDIUM_NAME_PARTS):
        reasons.append("name contains identifier-related term")
        return vtype, "MEDIUM" if value_conf != "HIGH" else "HIGH", reasons
    return vtype, value_conf, reasons


def candidates_from_request(req) -> list[Candidate]:
    out = []

    def add(name, value, location):
        vtype, conf, reasons = classify(name, value)
        if reasons:
            out.append(Candidate(name, str(value), location, vtype, conf, reasons))

    for name, value in req.query_params:
        add(name, value, "query")

    for name, value in req.form_params:
        add(name, value, "form")

    for name, value in req.multipart_fields:
        add(name, value, "multipart")

    for name, value in req.cookies.items():
        if name.lower() not in {"session", "sid", "csrftoken", "xsrf-token"}:
            add(name, value, "cookie")

    # Authorization fields are deliberately reported as sensitive metadata,
    # but their values are not printed by the CLI/report.
    for name, value in req.headers.items():
        if name.lower() in {"authorization", "proxy-authorization"}:
            out.append(Candidate(
                name=name,
                value="[REDACTED]",
                location="header",
                value_type="authorization",
                confidence="MEDIUM",
                reasons=["authorization-related header"],
            ))

    # Flatten JSON objects/lists into parameter paths.
    def walk(obj, prefix=""):
        if isinstance(obj, dict):
            for key, val in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                if isinstance(val, (dict, list)):
                    walk(val, path)
                else:
                    add(path, val, "json")
        elif isinstance(obj, list):
            for i, val in enumerate(obj):
                path = f"{prefix}[{i}]"
                if isinstance(val, (dict, list)):
                    walk(val, path)
                else:
                    add(path, val, "json")

    if req.json_data is not None:
        walk(req.json_data)

    # Analyze path segments. A segment gets a useful name based on the
    # preceding segment when possible, otherwise path_id.
    segments = [s for s in req.path.split("/") if s]
    for i, seg in enumerate(segments):
        if NUMERIC_RE.fullmatch(seg) or UUID_RE.fullmatch(seg) or OBJECTID_RE.fullmatch(seg):
            name = f"{segments[i-1]}_id" if i > 0 and re.fullmatch(r"[A-Za-z0-9_-]+", segments[i-1]) else "path_id"
            add(name, seg, "path")

    return out
