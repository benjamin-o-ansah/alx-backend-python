#!/usr/bin/env python3
"""
Unit tests for the utils module functions.
"""
import unittest
from unittest.mock import Mock, patch
from parameterized import parameterized
# Assuming utils is available in the environment path
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Tests the access_nested_map function from the utils module.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """
        Tests that access_nested_map returns the expected value
        for different nested maps and paths.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b'),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """
        Tests that access_nested_map raises a KeyError with the expected
        key name when the path cannot be traversed.
        """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """
    Tests the get_json function from the utils module, mocking HTTP calls.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload,
                      mock_requests_get):
        """
        Tests that utils.get_json returns the expected JSON data
        and ensures requests.get was called correctly.
        """
        # Configure the Mock object returned by requests.get
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_requests_get.return_value = mock_response

        # Call the function being tested
        result = get_json(test_url)

        # Test 1: Check if requests.get was called exactly once.
        mock_requests_get.assert_called_once_with(test_url)

        # Test 2: Check that the output is equal to the expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Tests the memoize decorator from the utils module.
    """
    def test_memoize(self):
        """
        Tests that when a method wrapped with @memoize is called,
        the decorated function is executed once.
        """
        class TestClass:
            """A class to test memoization on a property."""

            def a_method(self):
                """Method that should be called only once."""
                return 42

            @memoize
            def a_property(self):
                """Property that wraps a_method and is memoized."""
                return self.a_method()

        # Patch 'a_method' to track its calls
        with patch.object(TestClass, 'a_method') as mock_a_method:
            mock_a_method.return_value = 42

            # Instantiate the class
            test_instance = TestClass()

            # Call the property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assertions
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Key assertion: a_method must be called only once
            mock_a_method.assert_called_once()
