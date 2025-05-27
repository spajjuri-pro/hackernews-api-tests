# my-webapp-api-tests

Automated tests for the public Hacker News API, covering both functional and security (OWASP) scenarios.

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest
```

To generate an HTML report:

```bash
pytest -v --html=report.html --self-contained-html
```

---

## Test Coverage

### Functional Tests

- **Top Stories Retrieval:**  
  Ensures the `/topstories` endpoint returns a non-empty list of integer IDs.
- **Story Details:**  
  Fetches and validates details for a top story.
- **First Comment Retrieval:**  
  Validates the structure and content of the first comment for a top story.

### Security & OWASP Tests

- **Invalid, Empty, Null, and Non-Existent Item IDs:**  
  Checks API response for various invalid item IDs (expects `200 OK` with `null`).
- **SQL Injection Attempt:**  
  Ensures no sensitive data is leaked and no SQL is executed.
- **HTTP Security Headers:**  
  Verifies presence of headers like `Strict-Transport-Security`.
- **Verbose Error Messages:**  
  Ensures no sensitive error information is exposed.
- **Rate Limiting:**  
  Checks if the API enforces rate limiting (`429 Too Many Requests`).  
  _Note: Hacker News API may not enforce this; test may fail by design._

---

## Notes

- The Hacker News API typically returns `200 OK` with a `null` body for invalid or non-existent item IDs.
- Rate limiting is not always enforced; related tests may not pass.
- Tests are written using `pytest` and `requests`.

---
+-------------------+
|  Test Scripts     |  (test_hackernews_api.py)
+-------------------+
         |
         v
+-------------------+         +----------------+         +-------------------+
|   Pytest Runner   | <-----> |  HackerNews    | ----->  |   pytest-html     |
| (uses requests)   |  HTTP   |     API        | Results | (HTML Reporting)  |
+-------------------+         +----------------+         +-------------------+
         |
         v
+-------------------+
| Virtual Env &     |
| Requirements.txt  |
+-------------------+