#!/usr/bin/env python3
"""Integration tests for GithubOrgClient."""
import unittest
from unittest.mock import patch
from parameterized import parameterized_class
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos
from client import GithubOrgClient


@parameterized_class((
    "org_payload", "repos_payload", "expected_repos", "apache2_repos"
), [
    (org_payload, repos_payload, expected_repos, apache2_repos),
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos"""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        class MockResponse:
            def __init__(self, payload):
                self._payload = payload
            def json(self):
                return self._payload

        def side_effect(url):
            if url.endswith("/orgs/google"):
                return MockResponse(cls.org_payload)
            if url.endswith("/orgs/google/repos"):
                return MockResponse(cls.repos_payload)
            return MockResponse({})
        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)
