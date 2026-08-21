# RAVEN IDOR

<p align="center">
  <b>CLI-Based IDOR Analysis Assistant</b>
</p>

<p align="center">
  Analyze • Compare • Verify • Report
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-111111?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/Version-v1.0-orange?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status">
</p>

---

## 📖 About

**RAVEN IDOR** is a Python-based CLI security analysis tool designed to assist with **controlled and authorized web security testing**, particularly when analyzing identifiers and HTTP responses related to potential **IDOR (Insecure Direct Object Reference)** conditions.

RAVEN is designed with an **offline-first approach** and works well in CLI environments such as:

- 📱 Termux
- 🐧 Linux
- 🧪 Security Labs
- 🎯 CTF environments
- 🧰 Burp Suite workflows
- 🐛 Authorized bug bounty testing

> ⚠️ RAVEN IDOR does **not** automatically confirm vulnerabilities.
>
> Identifier detection and response differences are only **candidates for manual review**.

---

# 🧠 What is IDOR?

**IDOR (Insecure Direct Object Reference)** is an access-control issue that can occur when an application exposes a direct reference to an internal object without properly verifying whether the current user is authorized to access it.

Example:

```http
GET /api/profile/123 HTTP/1.1
Host: example.com

The value:

123

may represent a user, profile, document, order, or another object.

Another request could contain:

GET /api/profile/456 HTTP/1.1
Host: example.com

However:

123 ≠ vulnerability
456 ≠ vulnerability
Different response ≠ vulnerability

The important question is whether the application's authorization mechanism correctly controls access to those objects.

RAVEN helps identify potentially interesting identifiers and response differences so that a tester can perform manual verification.


---

✨ Features

Feature	Description

🔎 Request Parser	Analyze raw HTTP requests
🧩 Parameter Analysis	Identify interesting request parameters
🆔 Identifier Detection	Detect common ID patterns
📥 Response ID Discovery	Find identifiers already exposed in responses
🔬 Response Comparison	Compare two HTTP responses
▶️ Forward Mode	Send a single explicitly confirmed request
🔁 Repeater	Interactive CLI request workflow
📝 Report Generator	Generate Markdown security reports
🔐 Redaction	Help remove sensitive information
📱 Termux Friendly	Designed for mobile CLI environments
🧰 Burp Workflow	Designed to work with Burp request/response exports
📴 Offline Analysis	Most analysis does not require network access



---

🎯 Identifier Detection

RAVEN recognizes common identifier names such as:

id
user_id
account_id
profile_id
order_id
document_id
file_id
uid
product_id
transaction_id

It can also recognize common identifier-shaped values:

12345
550e8400-e29b-41d4-a716-446655440000
507f1f77bcf86cd799439011

Confidence Levels

Level	Meaning

🟢 HIGH	Strongly resembles an identifier
🟡 MEDIUM	Possibly an identifier
🔵 LOW	Weak identifier signal


> Confidence is not severity.

A HIGH confidence identifier does not mean a vulnerability exists.




---

📦 Requirements

Before installing RAVEN IDOR, make sure you have:

Python 3.10+

Git

Termux or Linux

Basic command-line knowledge


For Termux:

pkg update
pkg install git python


---

🚀 Installation

1. Clone the Repository

git clone https://github.com/43WildCard/Raven-IDOR-burpmobile-.git

Enter the directory:

cd raven-idor


---

2. Create Virtual Environment

python -m venv .venv

Activate it:

source .venv/bin/activate


---

3. Install RAVEN

python -m pip install -e .


---

4. Verify Installation

raven-idor --help

You should see the RAVEN CLI help menu.


---

⚡ Quick Start

A basic workflow looks like this:

Burp Suite
    │
    ▼
Save HTTP Request
    │
    ▼
RAVEN IDOR
    │
    ├── Parse
    ├── Params
    └── IDs
          │
          ▼
   Manual Review
          │
          ▼
 Authorized Response
          │
          ▼
      Compare
          │
          ▼
       Report


---

🛠️ Command Reference

Global Help

raven-idor --help

Display available commands and options.


---

🔎 Parse HTTP Request

Save a raw HTTP request:

request.txt

Example:

GET /api/profile/123?page=1 HTTP/1.1
Host: lab.example
Cookie: session=REDACTED

Run:

raven-idor parse request.txt

RAVEN will analyze the structure of the request.


---

🧩 Analyze Parameters

raven-idor params request.txt

Useful for identifying parameters such as:

id
user_id
account_id
profile_id
order_id
document_id

Example:

Parameters
────────────────────────────

page        → 1
profile_id  → 123


---

🆔 Detect Identifiers

raven-idor ids request.txt

Example:

Identifier Candidates
────────────────────────────────

Value       : 123
Location    : URL Path
Type        : Numeric ID
Confidence  : HIGH

Value       : 550e8400-e29b-41d4-a716-446655440000
Location    : Parameter
Type        : UUID
Confidence  : HIGH

Again:

Identifier ≠ IDOR


---

📥 Response ID Discovery

Save an authorized response:

response.txt

Then:

raven-idor response-ids response.txt

Example response:

{
  "user_id": 123,
  "order_id": 456
}

RAVEN may report:

Response Identifiers
────────────────────────

user_id   → 123
order_id  → 456

No Automatic Enumeration

RAVEN does not automatically generate:

123
124
125
126
127
...

and send them to a server.

The tool focuses on analyzing identifiers that are already present in the supplied request or response.


---

🔬 Compare Responses

Compare two responses:

raven-idor compare response1.txt response2.txt

RAVEN can compare:

HTTP status

Response size

Body similarity

Selected headers

Identifier-shaped values


Example:

Response Comparison
────────────────────────────

Status:
  Response 1 → 200
  Response 2 → 200

Size:
  Response 1 → 1842 bytes
  Response 2 → 1907 bytes

Body:
  Similarity → 91.4%

Identifiers:
  Difference detected

[!] MANUAL REVIEW REQUIRED

The result only indicates that something changed.

It does not prove IDOR.


---

▶️ Forward Mode

RAVEN provides an active Forward mode:

raven-idor --active forward request.txt --output response.txt

The tool requires explicit confirmation before sending the request.

Conceptually:

Request
   │
   ▼
Review
   │
   ▼
Confirmation
   │
   ▼
SEND ONCE
   │
   ▼
Response

The purpose is to prevent accidental repeated requests.


---

🔁 Repeater Mode

Start the CLI repeater:

raven-idor --active repeater request.txt --output response.txt

Example menu:

╭────────────────────────╮
│     RAVEN REPEATER     │
├────────────────────────┤
│ [r] Reload request     │
│ [s] Send once          │
│ [q] Quit               │
╰────────────────────────╯

Workflow:

1. Edit request.txt
2. Reload
3. Review request
4. Confirm sending
5. Send once
6. Analyze response


---

📝 Generate Report

Generate a Markdown report:

raven-idor report request.txt --output report.md

Example:

[+] Request analyzed
[+] Sensitive values redacted
[+] Report generated

Output:
report.md

The report can be used for security testing documentation.


---

🔐 Sensitive Data Redaction

Security testing data may contain sensitive information.

RAVEN is designed to help redact values such as:

Cookie
Authorization
Session ID
Access Token
Refresh Token
Password
API Key
Secrets

Example:

Authorization: Bearer REDACTED
Cookie: session=REDACTED

Always review the generated report before sharing it.


---

🧰 Burp Suite Workflow

RAVEN can be used together with Burp Suite.

┌───────────────────┐
│    Burp Suite     │
└─────────┬─────────┘
          │
          │ Save Request
          ▼
┌───────────────────┐
│   request.txt     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│    RAVEN IDOR     │
│                   │
│  parse            │
│  params           │
│  ids              │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Identifier        │
│ Candidates        │
└─────────┬─────────┘
          │
          ▼
     Manual Review
          │
          ▼
┌───────────────────┐
│ Authorized        │
│ Responses         │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ RAVEN compare     │
└─────────┬─────────┘
          │
          ▼
   Manual Assessment
          │
          ▼
┌───────────────────┐
│ report.md         │
└───────────────────┘


---

📋 Complete Example

# Clone
git clone https://github.com/43WildCard/Raven-IDOR-burpmobile-.git

# Enter project
cd Raven-IDOR-burpmobile-

# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate

# Install
python -m pip install -e .

# Check installation
raven-idor --help

# Parse request
raven-idor parse request.txt

# Analyze parameters
raven-idor params request.txt

# Detect identifiers
raven-idor ids request.txt

# Analyze response
raven-idor response-ids response.txt

# Compare responses
raven-idor compare response1.txt response2.txt

# Generate report
raven-idor report request.txt --output report.md


---

🧪 Example Request

GET /api/users/123/profile?page=1 HTTP/1.1
Host: lab.example
Accept: application/json
Cookie: session=REDACTED

Run:

raven-idor ids request.txt

Possible output:

╭─ Identifier Candidate ─────────╮
│ Value      : 123               │
│ Location   : URL Path          │
│ Type       : Numeric ID        │
│ Confidence : HIGH              │
╰────────────────────────────────╯

[!] Manual review required

This means:

> "This value looks like an identifier."



It does not mean:

> "This application contains IDOR."




---

🧠 Security Philosophy

RAVEN follows a simple workflow:

┌──────────┐
│ ANALYZE  │
└────┬─────┘
     ▼
┌──────────┐
│ IDENTIFY │
└────┬─────┘
     ▼
┌──────────┐
│ COMPARE  │
└────┬─────┘
     ▼
┌──────────┐
│ VERIFY   │
└────┬─────┘
     ▼
┌──────────┐
│ REPORT   │
└──────────┘

Not:

Scan → Enumerate → Attack

RAVEN is intended to assist a human tester rather than automatically declare vulnerabilities.


---

⚠️ Important

Identifier Found ≠ IDOR

/user/123

does not automatically indicate a vulnerability.

Different Response ≠ IDOR

A response may change because of:

Application logic

Object state

Caching

Error handling

Permissions

Session state

Other legitimate behavior


HIGH Confidence ≠ HIGH Severity

Confidence only represents how strongly a value resembles an identifier.


---

🛡️ Responsible Use

RAVEN IDOR is intended for:

✅ Security education

✅ CTF

✅ PortSwigger Web Security Academy

✅ Security labs

✅ Applications you own

✅ Authorized penetration testing

✅ Bug bounty programs that explicitly permit the activity



---

🚫 Do Not Use For

Do not use RAVEN IDOR to:

❌ Access systems without permission

❌ Perform unauthorized ID enumeration

❌ Brute-force identifiers

❌ Perform mass enumeration

❌ Access another user's private information

❌ Attack accounts belonging to other users

❌ Perform credential attacks

❌ Bypass authentication without authorization

❌ Bypass authorization controls outside an approved test

❌ Evade WAF/security controls

❌ Perform destructive testing

❌ Delete or modify unauthorized data

❌ Test targets outside bug bounty scope

❌ Collect or expose sensitive information



---

🔒 Data Protection

Always minimize the amount of sensitive data stored during testing.

Before sharing logs, requests, responses, or reports, remove:

Passwords
API Keys
Session Cookies
Access Tokens
Refresh Tokens
Authorization Headers
Personal Information
Secrets

Example:

Authorization: Bearer REDACTED
Cookie: session=REDACTED
X-API-Key: REDACTED


---

📜 Disclaimer

RAVEN IDOR is provided for educational and authorized security testing purposes only.

The developer does not authorize or encourage unauthorized access, data theft, privacy violations, destructive testing, or attacks against systems without explicit permission.

You are solely responsible for:

1. Confirming that the target is within scope.


2. Obtaining the necessary authorization.


3. Following the rules of the target or bug bounty program.


4. Protecting sensitive information.


5. Avoiding unnecessary impact on systems and users.



Use RAVEN only where you have permission to perform the testing.

> Always verify. Never assume. Test responsibly.




---

🐦‍⬛ RAVEN

██████╗  █████╗ ██╗   ██╗███████╗███╗   ██╗
██╔══██╗██╔══██╗██║   ██║██╔════╝████╗  ██║
██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║
██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║
██║  ██║██║  ██║ ╚████╔╝ ███████╗██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝

Analyze. Compare. Verify. Report.

RAVEN IDOR v1.0


---

⭐ Support

If you find RAVEN IDOR useful for authorized security research, consider giving the repository a ⭐ on GitHub.

Repository:
https://github.com/43WildCard/Raven-IDOR-burpmobile-


---

<p align="center">
  Made for learning, research, and responsible security testing.
</p>
```
