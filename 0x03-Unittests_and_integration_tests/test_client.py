#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class in client.py.
"""
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient
from unittest import TestCase


class TestGithubOrgClient(TestCase):
    """
    Tests the GithubOrgClient class methods.
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Tests that GithubOrgClient.org returns the correct value
        and that utils.get_json is called once with the correct URL.
        """
        # Create an instance of the client
        client = GithubOrgClient(org_name)

        # The expected URL that get_json should be called with
        expected_url = client.ORG_URL.format(org=org_name)

        # Call the org method
        client.org()

        # Assert that get_json was called exactly once with the expected URL
        mock_get_json.assert_called_once_with(expected_url)
    
    @patch('client.GithubOrgClient.org', new_callable=property)
    def test_public_repos_url(self, mock_org):
        """
        Tests that public_repos_url returns the correct URL
        from the mocked org payload.
        """
        mock_org.return_value = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos_url,
            "https://api.github.com/orgs/google/repos"
        )