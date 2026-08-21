import unittest

from raven_idor.reporter import redact_value
from raven_idor.parser import parse_request
from raven_idor.reporter import report_data


class RedactionTests(unittest.TestCase):
    def test_sensitive_name_redacted(self):
        self.assertEqual(redact_value("Authorization", "Bearer SECRET"), "[REDACTED]")
        self.assertEqual(redact_value("password", "hunter2"), "[REDACTED]")
        self.assertEqual(redact_value("api_key", "abc"), "[REDACTED]")

    def test_cookie_not_reported_as_value(self):
        r = parse_request(
            "GET / HTTP/1.1\r\nHost: lab\r\nCookie: session=TOPSECRET\r\n\r\n"
        )
        data = report_data(r)
        # Cookie itself may be parsed, but its value must never appear.
        text = str(data)
        self.assertNotIn("TOPSECRET", text)


if __name__ == "__main__":
    unittest.main()
