import unittest

from raven_idor.comparator import compare_responses
from raven_idor.parser import parse_response


class ComparatorTests(unittest.TestCase):
    def test_difference_is_not_confirmed_idor(self):
        a = parse_response("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nAlice")
        b = parse_response("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nBob")
        result = compare_responses(a, b)
        self.assertLess(result.body_similarity, 100)
        self.assertEqual(result.assessment, "MANUAL REVIEW REQUIRED")


if __name__ == "__main__":
    unittest.main()
