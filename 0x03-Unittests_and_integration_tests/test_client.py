#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class in client.py.
"""
from unittest import TestCase
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(TestCase):
    """
    Tests the GithubOrgClient class methods.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called once with the correct URL.
        """
        client = GithubOrgClient(org_name)
        expected_url = client.ORG_URL.format(org=org_name)

        client.org()

        mock_get_json.assert_called_once_with(expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        Tests GithubOrgClient.public_repos.
        """
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=property
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                "https://api.github.com/orgs/google/repos"
            )

            client = GithubOrgClient("google")
            repos = client.public_repos()

            self.assertEqual(repos, ["repo1", "repo2", "repo3"])

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/google/repos"
            )
