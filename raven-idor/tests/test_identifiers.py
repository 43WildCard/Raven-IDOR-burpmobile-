import unittest

from raven_idor.identifiers import candidates_from_request, classify
from raven_idor.parser import parse_request


class IdentifierTests(unittest.TestCase):
    def test_numeric_id_high(self):
        vtype, conf, _ = classify("user_id", "123")
        self.assertEqual(vtype, "numeric")
        self.assertEqual(conf, "HIGH")

    def test_uuid(self):
        vtype, conf, _ = classify(
            "reference",
            "550e8400-e29b-41d4-a716-446655440000"
        )
        self.assertEqual(vtype, "UUID")
        self.assertEqual(conf, "HIGH")

    def test_object_id(self):
        vtype, conf, _ = classify("object", "507f1f77bcf86cd799439011")
        self.assertEqual(vtype, "object-id")
        self.assertEqual(conf, "HIGH")

    def test_path_id(self):
        r = parse_request("GET /api/users/123/profile HTTP/1.1\r\nHost: lab\r\n\r\n")
        candidates = candidates_from_request(r)
        self.assertTrue(any(c.location == "path" and c.value == "123" for c in candidates))

    def test_json_id(self):
        r = parse_request(
            'POST /api HTTP/1.1\r\nContent-Type: application/json\r\n\r\n'
            '{"account_id": 77}'
        )
        candidates = candidates_from_request(r)
        self.assertTrue(any(c.name == "account_id" for c in candidates))


if __name__ == "__main__":
    unittest.main()
