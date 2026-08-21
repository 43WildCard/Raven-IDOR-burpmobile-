# RAVEN IDOR Analyzer

`raven-idor` is a small, offline-first Python CLI for analyzing raw HTTP
requests/responses exported from Burp Suite.

It is intended for authorized testing such as:

- Local labs
- CTFs
- PortSwigger Web Security Academy
- Bug bounty programs that explicitly permit the relevant testing
- Systems you own or are authorized to assess

## Safety model

The tool does **not** send HTTP requests.

It does not implement:

- brute-force ID enumeration
- mass scanning
- credential attacks
- authentication bypass
- WAF evasion/stealth
- automatic exploitation
- destructive actions

All active testing must be performed separately and within the target's
explicit rules.

A candidate's `HIGH`, `MEDIUM`, or `LOW` confidence only describes how strongly
the value resembles an identifier. It is **not** a vulnerability verdict.

## Requirements

Python 3.10+ is recommended. The application uses only the Python standard
library, so `requirements.txt` is intentionally empty.

## Termux installation

```sh
pkg update
pkg install python
git clone <your-repository-url> raven-idor
cd raven-idor

python -m venv .venv
. .venv/bin/activate

python -m pip install -e .
python -m unittest discover -s tests -v
```

If you do not want a virtual environment, you can run it directly from the
project directory:

```sh
python -m raven_idor.cli --help
```

## Burp Suite workflow

1. Perform testing only against an authorized target/lab.
2. In Burp Suite, copy/export a request as raw HTTP.
3. Save it as a local file, for example `request.txt`.
4. Run offline analysis:

```sh
raven-idor parse request.txt
raven-idor params request.txt
raven-idor ids request.txt
```

For responses, save two raw HTTP responses locally:

```text
response1.txt
response2.txt
```

Then compare them:

```sh
raven-idor compare response1.txt response2.txt
```

The comparison is descriptive. It does not prove that an authorization
boundary was bypassed.

## Commands

```text
raven-idor parse request.txt
raven-idor params request.txt
raven-idor ids request.txt
raven-idor compare response1.txt response2.txt
raven-idor report request.txt --output report.md
raven-idor --help
```

Options:

```text
--json       Machine-readable JSON where supported
--verbose    Reserved for future diagnostic output
--output     Output path
--no-color   Disable terminal styling; current release is already mostly plain
```

## Supported request content

The parser supports:

- Raw HTTP requests
- Query strings
- `application/x-www-form-urlencoded`
- JSON bodies
- Multipart field names/values when a boundary is available
- Cookies
- Authorization headers
- Absolute URLs and normal origin-form paths

## Detection heuristics

Identifier candidates are detected from:

- Parameter names such as `id`, `user_id`, `account_id`, `order_id`, `file_id`
- Numeric values
- UUID-shaped values
- MongoDB ObjectId-like 24-hex values
- Path segments
- JSON keys and nested JSON paths

Example:

```text
GET /api/users/123/profile HTTP/1.1
Host: lab.example
Cookie: session=REDACTED
User-Agent: Mozilla/5.0
```

A path segment such as `123` can be reported as a numeric candidate.

### Confidence

- **HIGH** — strong identifier naming or UUID/ObjectId pattern
- **MEDIUM** — plausible identifier pattern, such as a numeric value
- **LOW** — weak or generic signal

Confidence is heuristic only. It does not mean "confirmed IDOR".

## Response comparison

The comparator checks:

- HTTP status code
- Calculated response-body byte length
- Non-sensitive header changes
- Body similarity

Sensitive headers such as `Authorization`, `Cookie`, and `Set-Cookie` are
excluded from displayed header differences.

Example assessment:

```text
[!] MANUAL REVIEW REQUIRED

This tool does NOT confirm an IDOR.
Verify authorization behavior manually.
```

A difference can have many benign explanations: different timestamps,
personalization, cache state, CSRF values, feature flags, or normal application
logic.

## Reporting

Generate a Markdown report:

```sh
raven-idor report request.txt --output report.md
```

The report includes:

- Method
- Endpoint
- Parameter candidates
- Parameter location/type
- Confidence
- Observations
- Manual verification checklist

Sensitive values are redacted based on names such as:

- Cookie
- Authorization
- Token
- Password
- Secret
- API key
- Session

Do not paste real credentials or tokens into reports or issue trackers.

## Local dummy example

Request:

```text
POST /api/orders HTTP/1.1
Host: lab.example
Content-Type: application/json
Cookie: session=LOCAL_DUMMY

{"user_id":123,"order_id":456,"note":"hello"}
```

Then:

```sh
raven-idor params request.txt
raven-idor report request.txt --output report.md
```

## Responsible disclosure

Only test assets that are explicitly authorized. Follow the program's scope,
rate limits, prohibited actions, and data-handling requirements. Collect the
minimum evidence necessary and redact secrets from reports.

## Architecture

- `raven_idor/parser.py` — raw HTTP request/response parsing
- `raven_idor/parameters.py` — parameter analysis entry point
- `raven_idor/identifiers.py` — identifier heuristics and confidence scoring
- `raven_idor/comparator.py` — offline response comparison
- `raven_idor/reporter.py` — redacted Markdown reporting
- `raven_idor/cli.py` — terminal interface
- `tests/` — unit tests

## License

MIT
