RAVEN IDOR

RAVEN IDOR is a Python-based CLI tool designed to assist with controlled and authorized web security testing, particularly for analyzing identifiers and HTTP responses related to potential IDOR (Insecure Direct Object Reference) issues.

It is designed for CLI environments such as Termux and can be used alongside Burp Suite for security labs, CTFs, authorized testing, and bug bounty programs where testing is explicitly permitted.

«RAVEN IDOR does not automatically confirm IDOR vulnerabilities.
Identifiers and response differences are only candidates for manual security review.»

---

📖 What is IDOR?

IDOR (Insecure Direct Object Reference) is an access-control vulnerability that can occur when an application exposes a direct reference to an object, such as:

/user/123
/order/456
/document/789

or:

/api/profile/123
/api/profile/456

An identifier itself does not mean that an application is vulnerable.

The important question is whether the application properly verifies that the current user is authorized to access the requested object.

---

✨ Features

- HTTP request parsing
- Query parameter analysis
- Path parameter analysis
- JSON parameter analysis
- Form parameter analysis
- Cookie analysis
- Authorization header detection
- Common identifier detection
- UUID detection
- Numeric ID detection
- MongoDB ObjectId detection
- Response identifier discovery
- HTTP response comparison
- CLI Forward mode
- CLI Repeater mode
- Markdown report generation
- Sensitive information redaction
- Termux-friendly workflow
- Burp Suite workflow support
- Offline-first analysis

---

📦 Installation

Requirements

- Python 3.10+
- Git
- Termux / Linux / compatible Python environment

For Termux:

pkg update
pkg install git python

---

Clone the Repository

git clone https://github.com/43WildCard/Raven-IDOR-burpmobile-.git

Enter the directory:

cd Raven-IDOR-burpmobile-

---

Create Virtual Environment

python -m venv .venv

Activate it:

Linux / Termux

source .venv/bin/activate

If activation is successful, your shell should indicate that the virtual environment is active.

---

Install RAVEN IDOR

If the repository contains a Python package configuration such as "pyproject.toml":

python -m pip install -e .

Then verify:

raven-idor --help

If your project exposes the CLI under another executable name, check the installed package configuration or use:

python -m pip show raven-idor

---

🚀 Usage

Show Help

raven-idor --help

Show help for a specific command:

raven-idor <command> --help

---

🔎 Request Analysis

Save a raw HTTP request from Burp Suite as:

request.txt

Then parse the request:

raven-idor parse request.txt

---

Analyze Parameters

raven-idor params request.txt

This can help identify interesting parameters such as:

id
user_id
account_id
profile_id
order_id
document_id
file_id
product_id
transaction_id

---

Detect Identifiers

raven-idor ids request.txt

RAVEN can identify common identifier patterns such as:

123
456
12345
UUID
MongoDB ObjectId

Example:

GET /api/profile/123 HTTP/1.1
Host: lab.example

RAVEN may identify:

Value      : 123
Location   : Path
Type       : Numeric Identifier
Confidence : HIGH

«HIGH confidence does not mean HIGH severity.
It only indicates that the value strongly resembles an identifier.»

---

📥 Response Analysis

Save an authorized HTTP response as:

response.txt

Then run:

raven-idor response-ids response.txt

This can identify object references already visible inside the response.

For example:

{
  "user_id": 123,
  "order_id": 456
}

RAVEN can flag:

user_id   → 123
order_id  → 456

RAVEN does not automatically enumerate:

123
124
125
126
127
...

---

🔬 Compare Responses

Compare two responses:

raven-idor compare response1.txt response2.txt

RAVEN can help compare:

- HTTP status
- Response size
- Body similarity
- Selected headers
- Identifier-shaped values

Example conceptual result:

[!] MANUAL REVIEW REQUIRED

This means the responses contain differences worth investigating.

It does not mean that an IDOR vulnerability has been confirmed.

---

▶️ Forward Mode

RAVEN provides an active Forward mode for sending a single request:

raven-idor --active forward request.txt --output response.txt

The active mode requires explicit user confirmation before sending.

Conceptually:

Request
   ↓
RAVEN
   ↓
Confirmation
   ↓
SEND ONCE
   ↓
Response

RAVEN does not perform automatic repeated requests in Forward mode.

---

🔁 Repeater Mode

Start the CLI repeater:

raven-idor --active repeater request.txt --output response.txt

Typical controls:

[r] Reload request
[s] Send once
[q] Quit

Workflow:

1. Edit request.txt
2. Open/reload the request
3. Review the request
4. Confirm sending
5. Send once
6. Analyze the response

Every request should be sent intentionally and only against an authorized target.

---

📝 Generate a Report

Generate a Markdown report:

raven-idor report request.txt --output report.md

The report is intended to help document security testing results.

Sensitive information should be redacted, including:

Cookie
Authorization
Session ID
Access Token
Refresh Token
Password
API Key
Secrets

Always review the generated report before sharing it.

---

🧪 Complete Example Workflow

A basic authorized testing workflow:

# Clone
git clone https://github.com/43WildCard/Raven-IDOR-burpmobile-.git

# Enter project
cd Raven-IDOR-burpmobile-

# Create environment
python -m venv .venv

# Activate environment
source .venv/bin/activate

# Install
python -m pip install -e .

# Check installation
raven-idor --help

# Analyze request
raven-idor parse request.txt

# Analyze parameters
raven-idor params request.txt

# Find identifiers
raven-idor ids request.txt

# Analyze response
raven-idor response-ids response.txt

# Compare authorized responses
raven-idor compare response1.txt response2.txt

# Generate report
raven-idor report request.txt --output report.md

---

🔗 Burp Suite Workflow

RAVEN IDOR can be used alongside Burp Suite:

┌───────────────┐
│   Burp Suite  │
└───────┬───────┘
        │
        ▼
 Save HTTP Request
        │
        ▼
┌─────────────────┐
│   RAVEN IDOR    │
│     params      │
│       ids       │
└────────┬────────┘
         │
         ▼
Identifier Candidates
         │
         ▼
 Manual Verification
         │
         ▼
Authorized Responses
         │
         ▼
┌─────────────────┐
│ RAVEN compare   │
└────────┬────────┘
         │
         ▼
 Manual Assessment
         │
         ▼
┌─────────────────┐
│  Generate Report │
└─────────────────┘

RAVEN is an analysis assistant, not an automatic vulnerability confirmation system.

---

⚠️ Disclaimer

RAVEN IDOR is provided for educational, research, CTF, security lab, and authorized security testing purposes only.

You are responsible for ensuring that you have explicit permission to test the target.

Only test:

- Systems you own
- Security labs
- CTF environments
- Authorized penetration-testing targets
- Bug bounty targets that explicitly allow your testing activity

Do NOT use RAVEN IDOR to:

- Access systems without authorization
- Brute-force identifiers
- Perform mass enumeration
- Access another user's private data
- Attack accounts belonging to other users
- Perform credential attacks
- Bypass authentication or authorization without permission
- Evade WAF or security controls
- Perform destructive testing
- Delete or modify unauthorized data
- Test targets outside a bug bounty scope
- Expose or distribute sensitive information

---

🔐 Responsible Testing

Always follow these principles:

AUTHORIZED
    ↓
MINIMAL REQUESTS
    ↓
MINIMAL DATA
    ↓
MANUAL VERIFICATION
    ↓
RESPONSIBLE REPORTING

Remember:

Identifier found ≠ IDOR

Response changed ≠ IDOR

High confidence ≠ High severity

RAVEN result ≠ Confirmed vulnerability

The final determination must be based on the application's actual authorization behavior and the rules of the authorized testing environment.

---

🐦‍⬛ RAVEN IDOR

Analyze.
Compare.
Verify.
Report.

Never assume.
Always verify.

RAVEN IDOR v1 — CLI security analysis for controlled and authorized testing.
