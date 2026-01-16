#!/usr/bin/env python3
"""
Unit tests for the GithubOrgClient class in client.py.
"""
from unittest import TestCase
from unittest.mock import patch, PropertyMock,MagicMock
from parameterized import parameterized,parameterized_class
from client import GithubOrgClient
import fixtures

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

    @parameterized.expand([
        (
            {"license": {"key": "my_license"}},
            "my_license",
            True,
        ),
        (
            {"license": {"key": "other_license"}},
            "my_license",
            False,
        ),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Tests GithubOrgClient.has_license.
        """
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        Tests GithubOrgClient.public_repos.
        """
        mock_get_json.return_value = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock
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

@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (
            fixtures.org_payload,
            fixtures.repos_payload,
            fixtures.expected_repos,
            fixtures.apache2_repos,
        )
    ]
)
class TestIntegrationGithubOrgClient(TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    """

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # Side effect to return fixture based on URL
        def get_side_effect(url, *args, **kwargs):
            # mock_resp = MagicMock()
            # if url == "https://api.github.com/orgs/google":
            #     mock_resp.json.return_value = cls.org_payload
            # elif url == "https://api.github.com/orgs/google/repos":
            #     mock_resp.json.return_value = cls.repos_payload
            # else:
            #     mock_resp.json.return_value = {}
            # return mock_resp
            """ Returns a mock response object with a json method """
            mock_response = MagicMock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            return mock_response
        cls.mock_get.side_effect = get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher for requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos without license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with apache-2.0 license filter"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )

print(fixtures.org_payload)
print(fixtures.repos_payload)
print(fixtures.expected_repos)
print(fixtures.apache2_repos)