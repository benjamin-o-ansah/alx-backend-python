# 🐙 GitHub Organization Client Project

A robust and well-tested Python client designed to interact with the GitHub API, focusing on retrieving organization details and their public repositories.

This project emphasizes industry best practices in software development, including utility function development, comprehensive unit testing, and dependency management.

## 🛠️ Project Structure

The project is structured to separate concerns, keeping utility functions, fixtures (mock data), the main client logic, and testing separate.

| File | Description |
| :--- | :--- |
| `client.py` | Contains the main `GithubOrgClient` class for interacting with the GitHub API. Includes methods for fetching organization data and public repositories, utilizing memoization. |
| `utils.py` | A library of generic utility functions, including `access_nested_map`, `get_json` (for API calls), and `memoize` (a decorator for caching method calls). |
| `fixtures.py` | Stores static JSON data payloads (`TEST_PAYLOAD`) used for mocking API responses in unit tests, ensuring tests are fast and reliable. |
| `test_utils.py` (or similar) | **Unit tests** for the utility functions in `utils.py`, ensuring their core functionality is robust (e.g., the `access_nested_map` test). |

## ✨ Key Features & Concepts

This project demonstrates proficiency in several advanced Python and engineering concepts:

### 1. Advanced Python Utilities
* **Nested Map Access:** The `access_nested_map` function provides a safe way to retrieve values from deeply nested dictionaries using a path sequence.
* **Memoization:** The `@memoize` decorator is implemented to cache the results of expensive method calls (like fetching API data), significantly improving performance by preventing redundant network requests.

### 2. Robust Unit Testing
* **`unittest` Framework:** Uses Python's standard `unittest` library for creating structured test cases.
* **`parameterized` Testing:** Leverages the `parameterized` library to run a single test method multiple times with different input data and expected outcomes (as seen in `TestAccessNestedMap`).
* **Fixtures and Mocking:** Utilizes static data in `fixtures.py` and is prepared for mocking external dependencies (like network calls) to ensure tests are isolated and deterministic.

### 3. API Client Design
* **`GithubOrgClient`:** Designed with properties and memoized methods (`org`, `repos_payload`) to efficiently handle repeated data retrieval from the GitHub API.

## ⚙️ Setup and Installation

### Prerequisites

* Python 3.8+
* `requests` library (for `utils.get_json`)
* `parameterized` library (for unit tests)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:benjamin-o-ansah/alx-backend-python.git
    cd 0x03-Unittests_and_integration_tests
    ```

2.  **Install dependencies:**
    ```bash
    pip install requests parameterized
    ```

## 🧪 Running Tests

All unit tests are designed to be run using the standard Python `unittest` module runner.

To execute the tests:

```bash
python3 -m unittest discover