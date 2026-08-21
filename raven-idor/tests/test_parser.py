import unittest

from raven_idor.parser import parse_request, parse_response


class ParserTests(unittest.TestCase):
    def test_query_and_cookies(self):
        raw = (
            "GET /api/users/123/profile?page=1 HTTP/1.1\r\n"
            "Host: lab.example\r\n"
            "Cookie: session=SECRET; theme=dark\r\n\r\n"
        )
        r = parse_request(raw)
        self.assertEqual(r.method, "GET")
        self.assertEqual(r.path, "/api/users/123/profile")
        self.assertEqual(r.query_params, [("page", "1")])
        self.assertEqual(r.cookies["session"], "SECRET")

    def test_json(self):
        raw = (
            "POST /api/profile HTTP/1.1\r\n"
            "Content-Type: application/json\r\n\r\n"
            '{"user_id": 123, "name": "Alice"}'
        )
        r = parse_request(raw)
        self.assertEqual(r.json_data["user_id"], 123)

    def test_form(self):
        raw = (
            "POST /login HTTP/1.1\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n\r\n"
            "user_id=42&name=Alice"
        )
        r = parse_request(raw)
        self.assertEqual(r.form_params, [("user_id", "42"), ("name", "Alice")])

    def test_response(self):
        raw = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nhello"
        r = parse_response(raw)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.body, "hello")


if __name__ == "__main__":
    unittest.main()
