from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .comparator import compare_responses
from .identifiers import candidates_from_request
from .parser import parse_request, parse_response
from .reporter import report_data, write_report

BANNER = """╭──────────────────────────────╮
│       RAVEN IDOR ANALYZER    │
╰──────────────────────────────╯"""


def _read(path):
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _print_candidate(c, i):
    print(f"[{i}] {c.location.upper()}")
    print(f"    Name: {c.name}")
    print(f"    Value: {c.value}")
    print(f"    Type: {c.value_type}")
    print(f"    Confidence: {c.confidence}")
    if c.reasons:
        print(f"    Reason: {', '.join(c.reasons)}")
    print()


def _request_summary(req):
    print(f"[+] Method: {req.method}")
    print(f"[+] Endpoint: {req.path}{('?' + req.query) if req.query else ''}")
    print(f"[+] Headers: {len(req.headers)}")
    print(f"[+] Body bytes: {len(req.body.encode('utf-8'))}")


def cmd_parse(args):
    req = parse_request(_read(args.file))
    if args.json:
        print(json.dumps({
            "method": req.method,
            "target": req.target,
            "version": req.version,
            "path": req.path,
            "query": req.query,
            "headers": req.headers,
            "query_params": req.query_params,
            "form_params": req.form_params,
            "json": req.json_data,
            "cookies": {k: "[REDACTED]" for k in req.cookies},
            "multipart_fields": req.multipart_fields,
        }, indent=2))
        return
    print(BANNER)
    print(f"\n[+] Request: {args.file}")
    _request_summary(req)


def cmd_params(args):
    req = parse_request(_read(args.file))
    candidates = candidates_from_request(req)
    if args.json:
        print(json.dumps([c.__dict__ for c in candidates], indent=2))
        return
    print(BANNER)
    print(f"\n[+] Request: {args.file}")
    _request_summary(req)
    print("\n[PARAMETERS]\n")
    if not candidates:
        print("No interesting identifier-like parameters detected.")
        return
    for i, c in enumerate(candidates, 1):
        _print_candidate(c, i)
    print("[!] Potential authorization-sensitive identifiers are candidates for manual review only.")


def cmd_ids(args):
    req = parse_request(_read(args.file))
    candidates = candidates_from_request(req)
    ids = [c for c in candidates if c.value_type in {"numeric", "UUID", "object-id"}]
    if args.json:
        print(json.dumps([c.__dict__ for c in ids], indent=2))
        return
    print(BANNER)
    print("\n[IDENTIFIER CANDIDATES]\n")
    if not ids:
        print("No numeric, UUID, or ObjectId-like candidates detected.")
        return
    for i, c in enumerate(ids, 1):
        _print_candidate(c, i)


def cmd_compare(args):
    a = parse_response(_read(args.response_a))
    b = parse_response(_read(args.response_b))
    result = compare_responses(a, b)
    data = {
        "status": {"A": result.status_a, "B": result.status_b},
        "content_length": {"A": result.content_length_a, "B": result.content_length_b},
        "body_similarity_percent": round(result.body_similarity, 2),
        "changed_headers": result.changed_headers,
        "observations": result.suspicious_observations,
        "assessment": result.assessment,
    }
    if args.json:
        print(json.dumps(data, indent=2))
        return
    print(BANNER)
    print("\n[+] Response comparison\n")
    print(f"Status:\nA: {result.status_a}\nB: {result.status_b}\n")
    print(f"Content-Length (calculated body bytes):\nA: {result.content_length_a}\nB: {result.content_length_b}\n")
    print(f"Body similarity: {result.body_similarity:.1f}%\n")
    if result.changed_headers:
        print("Changed non-sensitive headers:")
        for h in result.changed_headers:
            print(f"- {h}")
    if result.suspicious_observations:
        print("\nPotential difference detected:")
        for item in result.suspicious_observations:
            print(f"- {item}")
    else:
        print("No material response difference detected.")
    print(f"\nAssessment:\n[!] {result.assessment}")
    print("\nThis tool does NOT confirm an IDOR. Verify authorization behavior manually.")


def cmd_report(args):
    request = parse_request(_read(args.file))
    output = args.output or "raven-idor-report.md"
    write_report(args.file, output)
    if args.json:
        print(json.dumps(report_data(request), indent=2))
    else:
        print(f"[+] Report written to {output}")


def build_parser():
    p = argparse.ArgumentParser(
        prog="raven-idor",
        description="Offline Burp HTTP request/response analyzer for authorized security testing.",
    )
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON where supported.")
    p.add_argument("--verbose", action="store_true", help="Reserved for additional diagnostic output.")
    p.add_argument("--output", help="Output path (primarily useful with report).")
    p.add_argument("--no-color", action="store_true", help="Disable terminal styling (reserved for future styling).")

    sub = p.add_subparsers(dest="command", required=True)

    for name, func, help_text in [
        ("parse", cmd_parse, "Parse an exported raw HTTP request."),
        ("params", cmd_params, "List interesting parameters and identifier candidates."),
        ("ids", cmd_ids, "Show numeric/UUID/ObjectId-like candidates."),
    ]:
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("file")
        sp.set_defaults(func=func)

    sp = sub.add_parser("compare", help="Compare two saved raw HTTP responses.")
    sp.add_argument("response_a")
    sp.add_argument("response_b")
    sp.set_defaults(func=cmd_compare)

    sp = sub.add_parser("report", help="Generate a Markdown analysis report.")
    sp.add_argument("file")
    sp.add_argument("--output", default=None)
    sp.set_defaults(func=cmd_report)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"[!] Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
