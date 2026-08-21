from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from email.parser import BytesParser
from email.policy import default
from urllib.parse import parse_qsl, urlsplit


@dataclass
class HTTPRequest:
    method: str
    target: str
    version: str
    headers: dict[str, str]
    body: str
    path: str
    query: str
    query_params: list[tuple[str, str]] = field(default_factory=list)
    form_params: list[tuple[str, str]] = field(default_factory=list)
    json_data: object | None = None
    cookies: dict[str, str] = field(default_factory=dict)
    multipart_fields: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class HTTPResponse:
    version: str
    status_code: int
    reason: str
    headers: dict[str, str]
    body: str


def _headers_from_lines(lines: list[str]) -> dict[str, str]:
    headers = {}
    for line in lines:
        if not line.strip() or ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def _split_http_message(raw: str):
    # Normalize only line endings; preserve body content.
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    head, sep, body = raw.partition("\n\n")
    lines = head.split("\n")
    return lines, body if sep else ""


def parse_cookies(value: str) -> dict[str, str]:
    result = {}
    for part in value.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, val = part.split("=", 1)
        result[name.strip()] = val.strip()
    return result


def _parse_multipart(body: str, content_type: str) -> list[tuple[str, str]]:
    match = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type, re.I)
    if not match:
        return []
    boundary = match.group(1) or match.group(2)
    delimiter = "--" + boundary
    fields = []
    for part in body.split(delimiter):
        part = part.strip("\r\n- ")
        if not part:
            continue
        phead, sep, pbody = part.replace("\r\n", "\n").partition("\n\n")
        if not sep:
            continue
        m = re.search(r'name="([^"]+)"', phead, re.I)
        if m:
            fields.append((m.group(1), pbody.rstrip("\r\n")))
    return fields


def parse_request(raw: str) -> HTTPRequest:
    lines, body = _split_http_message(raw)
    if not lines:
        raise ValueError("Empty HTTP request")

    request_line = lines[0].split()
    if len(request_line) < 3 or not request_line[0].isalpha():
        raise ValueError("Invalid HTTP request line")

    method, target, version = request_line[0], request_line[1], request_line[2]
    headers = _headers_from_lines(lines[1:])
    parsed = urlsplit(target)

    # For Burp exports, target may be an absolute URL or an origin-form path.
    path = parsed.path or "/"
    query = parsed.query
    query_params = parse_qsl(query, keep_blank_values=True)

    content_type = headers.get("Content-Type", "")
    form_params = []
    json_data = None
    multipart_fields = []

    if "application/x-www-form-urlencoded" in content_type.lower():
        form_params = parse_qsl(body, keep_blank_values=True)
    elif "application/json" in content_type.lower():
        try:
            json_data = json.loads(body) if body.strip() else None
        except json.JSONDecodeError:
            json_data = None
    elif "multipart/form-data" in content_type.lower():
        multipart_fields = _parse_multipart(body, content_type)

    cookies = parse_cookies(headers.get("Cookie", ""))

    return HTTPRequest(
        method=method,
        target=target,
        version=version,
        headers=headers,
        body=body,
        path=path,
        query=query,
        query_params=query_params,
        form_params=form_params,
        json_data=json_data,
        cookies=cookies,
        multipart_fields=multipart_fields,
    )


def parse_response(raw: str) -> HTTPResponse:
    lines, body = _split_http_message(raw)
    if not lines:
        raise ValueError("Empty HTTP response")
    status = lines[0].split(None, 2)
    if len(status) < 2 or not status[0].startswith("HTTP/"):
        raise ValueError("Invalid HTTP response status line")
    try:
        code = int(status[1])
    except ValueError as exc:
        raise ValueError("Invalid HTTP status code") from exc
    reason = status[2] if len(status) > 2 else ""
    headers = _headers_from_lines(lines[1:])
    return HTTPResponse(status[0], code, reason, headers, body)
