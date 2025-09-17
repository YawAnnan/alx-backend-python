#!/usr/bin/env python3
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for access_nested_map"""

    # already implemented tests...
    # (leave them as they are)


class TestGetJson(unittest.TestCase):
    """Unit tests for get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url, test_payload):
        """Test that get_json returns expected payload with mocked requests.get"""
        # Patch requests.get
        with patch("utils.requests.get") as mock_get:
            # Configure the mock to return a response with .json() method
            mock_response = Mock()
            mock_response.json.return_value = test_payload
            mock_get.return_value = mock_response

            result = get_json(test_url)

            # Verify requests.get was called once with test_url
            mock_get.assert_called_once_with(test_url)

            # Verify result is the expected payload
            self.assertEqual(result, test_payload)


if __name__ == "__main__":
    unittest.main()
