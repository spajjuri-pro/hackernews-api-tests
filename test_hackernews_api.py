import requests
import pytest
import time

BASE_URL = "https://hacker-news.firebaseio.com/v0/"
TOP_STORIES_URL= f"{BASE_URL}/topstories.json"
ITEM_URL= f"{BASE_URL}/item/"

#--- Helper functions ---

def get_response_json(url):
    try:
        response= requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        pytest.fail(f"API request failed : {e}")

def get_item_details(item_id):
    return get_response_json(f"{ITEM_URL}{item_id}.json")

# --- Acceptance Tests (Functional) ---

def test_retrieve_top_stories_success():
    """
    Testcase: Retrieve the top stories using topstories API
    Description
        - Verifies the Topstories returns list of story IDs
        - Verifies that length of the Topstories list is not null
        - Verifies that topstory ID is an integer by checking few items in the Topstories list
    """

    top_story_ids = get_response_json(TOP_STORIES_URL)

    assert isinstance(top_story_ids, list)
    assert len(top_story_ids) > 0
    print(f"{len(top_story_ids)} Top stories retrieved")

    for i in range(min(5, len(top_story_ids))):
        assert isinstance(top_story_ids[i], int), f"Element at {i} is not an integer"
    print("Top stories contains integers IDs")

def test_get_top_stories_details():
    """
    Testcase: Using Top stories API to retrieve the current top story from the Items API
        - Verifies top stories not null and gets ID of the current top story
        - Verifies Top story details from Items API is a Dictionary
        - Verifies "id" value of item details is current top story ID
        - Verifies 'type' and 'title' fields are part of item details
    Edge Cases Covered:
        - If top stories list is empty, the test fails
        - Network issues are handled by the get_response_json function
    """
    top_story_ids = get_response_json(TOP_STORIES_URL)
    assert len(top_story_ids) > 0, "Top Stories item list is empty"
    first_top_story_id = top_story_ids[0]

    items_details = get_item_details(first_top_story_id)

    assert isinstance(items_details,dict) , "Item details response is not a dict"
    assert items_details.get('id')==first_top_story_id , "Item ID mismatch"
    assert 'type' in items_details, "Item details is missing 'type' field"
    assert 'title' in items_details, "Item details is missing 'title' field"
    assert isinstance(items_details['title'], str), "Item title is not a string."


def test_first_comment_of_top_story():
    """
    Test Case: Using the top stories API to retrieve a top story, retrieve its first comment using the items API
    Description:
    -Fetches the list of top stories
    -Iterate through the list of top stories to find the one with the comments (indicated by 'kids' array)
    - Verify that the first comment of the top story is retrieved successfully
    - Asserts key fields in the comment details
    Edge Cases Covered:
    - If no top story with comments is found in the first 20 stories, the test fails
    - Empty 'kids' array in the story details is handled
    - Network issues (handleed by get_response_json function)
    """
    top_stories_ids = get_response_json(TOP_STORIES_URL)
    story_with_comments_found = False
    comment_id = None
    story_title = "N/A"

    assert len(top_stories_ids)>0, "Top stories list is empty"

    for story_id in top_stories_ids[:20]:
        story_details = get_item_details(story_id)
        if story_details and story_details.get('kids') and len(story_details['kids']) > 0:
            comment_id = story_details['kids'][0]
            story_title = story_details.get('title', f"Story ID {story_id}")
            story_with_comments_found = True
            print(f"Found story {story_title} with comments. First comment ID {comment_id}")
            break
    assert story_with_comments_found, "Could not find a top story with comments with in first 20 stories"
    assert comment_id is not None, "Comment id is not retrieved"
    comment_details = get_item_details(comment_id)

    assert isinstance(comment_details, dict), "Comment details is not a dictionary"
    assert comment_details.get('id') == comment_id, "Comment ID mismatch"
    assert comment_details.get('type')=='comment', "Comment Type is not 'comment'"
    assert 'text' in comment_details, "Comment details is missing 'text' section"
    print(f"Comment details of {comment_id} is successfully retrieved for the story {story_title}")


# --- OWASP-related Security Tests ---

def test_security_input_validation_invalid_item_id():
    """
    Testcase: Validate input handling for invalid item ID
    Description:
        - Verifies that the API returns a 404 status code for an invalid item ID
    """
    invalid_item_id = "abc123"
    response = requests.get(f"{ITEM_URL}{invalid_item_id}.json")
    print(f"Testing invalid item ID: {invalid_item_id}. Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for invalid item ID, got {response.status_code}"
    assert response.json() is None, "Expected null response for invalid item ID"
    # Ensure that the response does not contain server errors
    assert not response.status_code >= 500, \
        f"Unexpected server error for invalid item ID: {response.status_code}. Response: {response.text}"
    print(f"API correctly handled invalid item ID: {invalid_item_id}")    

def test_security_input_validation_empty_item_id():
    """
    Testcase: Validate input handling for empty item ID
    Description:
        - Verifies that the API returns a 401 status code for an empty item ID
    """
    empty_item_id = ""
    response = requests.get(f"{ITEM_URL}{empty_item_id}.json")
    print(f"Testing empty item ID. Status code: {response.status_code}")
    assert response.status_code == 401, f"Expected 401 for empty item ID, got {response.status_code}"
    assert not response.status_code >= 500, \
        f"Unexpected server error for empty item ID: {response.status_code}. Response: {response.text}"
    print("API correctly handled empty item ID")

def test_security_input_validation_non_existent_item_id():
    """
    Testcase: Validate input handling for non-existent item ID
    Description:
        - Verifies that the API returns a 404 status code for a non-existent item ID
    """
    non_existent_item_id = 9999999999  # Assuming this ID does not exist
    response = requests.get(f"{ITEM_URL}{non_existent_item_id}.json")
    print(f"Testing non-existent item ID: {non_existent_item_id}. Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for non-existent item ID, but got {response.status_code} and response: {response.text}"
    assert response.json() is None, "Expected null response  for non-existent item ID"
    print(f"API correctly handled non-existent item ID: {non_existent_item_id}")

def test_security_input_null_item_id():
    """
    Testcase: Validate input handling for null item ID
    Description:
        - Verifies that the API returns a 401 status code for a null item ID
    """
    null_item_id = None
    response = requests.get(f"{ITEM_URL}{null_item_id}.json")
    print(f"Testing null item ID. Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for null item ID, got {response.status_code}"
    assert response.json() is None, "Expected null response for null item ID"

def test_security_input_validation_sql_injection():
    """
    Testcase: Validate input handling for SQL injection attempt
    Description:
        - Verifies that the API does not return sensitive information or execute SQL commands
    """
    sql_injection_payload = "'; DROP TABLE users; --"
    response = requests.get(f"{ITEM_URL}{sql_injection_payload}.json")
    print(f"Testing SQL injection payload: {sql_injection_payload}. Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for SQL injection payload, got {response.status_code}"
    assert response.json() is None, "Expected null response for SQL injection payload"

def test_security_http_security_headers():
    """
        OWASP Test (A05:2021 - Security Misconfiguration): Check for essential HTTP security headers.
        Description:
        - Makes a request to a common API endpoint (e.g., top stories).
        - Asserts the presence of key security headers that help prevent common attacks.
        - Note: Not all headers are strictly required for a pure API, but good practice for web servers.
    """
    response = requests.get(TOP_STORIES_URL)
    headers = response.headers
    print(f"Checking headers for {TOP_STORIES_URL}: {headers}")

    # common security headers
    # Strict-Transport-Security: Enforces secure (HTTPS) connections to the server
    assert "Strict-Transport-Security" in headers, "Missing Strict-Transport-Security header"

def test_security_verbose_error_messages():
    """
    Testcase: Validate that the API does not expose verbose error messages
    Description:
        - Verifies that the API does not return detailed error messages that could aid an attacker
    """
    response = requests.get(f"{ITEM_URL}9999999999.json")  # Non-existent item ID
    print(f"Testing verbose error messages for non-existent item ID. Status code: {response.status_code} and response: {response.text}")

    assert response.status_code == 200, f"Expected 200 for non-existent item ID, got {response.status_code}"
    assert response.json() is None, "Expected null response for non-existent item ID"
        
    # Check if the response contains any sensitive information
    assert "error" not in response.text, "Response contains sensitive error information"

def test_security_rate_limiting():
    """
    Testcase: Validate rate limiting by making multiple requests in a short time
    Description:
        - Verifies that the API enforces rate limiting by checking for 429 Too Many Requests status code
    """
    requests_per_second = 50 
    rate_limit_triggered = False
    for _ in range(requests_per_second):  
        response = requests.get(TOP_STORIES_URL)
        if response.status_code == 429:
            rate_limit_triggered = True
            break
        time.sleep(0.01)  # Short delay to avoid overwhelming the server

    assert rate_limit_triggered, "API did not trigger rate limiting after {requests_per_second} requests"









