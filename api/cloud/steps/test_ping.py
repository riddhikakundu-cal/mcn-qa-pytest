import os
import re
import pytest
import requests
import logging
from pathlib import Path
from typing import Final
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers


LOG_FILE: Final = Path(__file__).parent / "test_ping.log"


logging.getLogger().handlers.clear()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8", mode="w"),
        logging.StreamHandler(),
    ],
    force=True  
)

logger = logging.getLogger("ping-tests")


scenarios('../run_test_ping.feature')

response = {}

@given("the query parameters are valid")
def valid_query_params(source_ip, destination_ip, ping_type):
    logger.info("Setting valid query parameters")
    response['params'] = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    response['expected_destination'] = destination_ip

@given(parsers.parse('the query parameters are missing "{param}"'))
def missing_query_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Removing query parameter: {param}")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    query.pop(param, None)
    response['params'] = query

@given(parsers.parse('the query parameters are invalid "{param}"'))
def invalid_query_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Making query parameter '{param}' invalid")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    if param == "destination":
        query["destination"] = "invalid_ip"
    response['params'] = query

@given(parsers.parse('the query parameters have special characters in "{param}"'))
def special_characters_in_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Inserting special characters in param: {param}")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    query[param] = "!@#type$%"
    response['params'] = query

@given("the request headers are valid")
def valid_headers(tenant_id):
    logger.info("Setting valid request headers")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }

@given(parsers.parse('the request headers are missing "{header}"'))
def missing_header(header, tenant_id):
    logger.info(f"Removing request header: {header}")
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    headers.pop(header, None)
    response['headers'] = headers

@given('the request headers contain "X-TenantID" with invalid value')
def invalid_x_tenantid():
    logger.info("Setting invalid X-TenantID header")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": "!!invalid##"
    }

@when("the API request is sent")
def send_request(ping_api_url):
    logger.info("Sending API request with params and headers")
    try:
        resp = requests.get(ping_api_url, headers=response.get('headers', {}), params=response.get('params', {}))
        response['resp'] = resp
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@when("I trigger ping metrics request using env config")
def ping_metrics_from_env(ping_api_url, source_ip, destination_ip, tenant_id, ping_type):
    logger.info("Triggering ping metrics request using dynamic source/destination IPs")
    params = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    try:
        resp = requests.get(ping_api_url, headers=headers, params=params)
        response['resp'] = resp
        response['expected_destination'] = destination_ip
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@then(parsers.parse('the response code should be {expected_code:d}'))
@then(parsers.parse('the ping metrics API response code should be {expected_code:d}'))
def check_status_code(expected_code):
    assert response['resp'] is not None, f"Request failed: {response.get('error')}"
    actual_code = response['resp'].status_code
    logger.info(f"Asserting status code: expected={expected_code}, actual={actual_code}")
    if actual_code != expected_code:
        logger.warning("Full response body: %s", response['resp'].text)
    assert actual_code == expected_code

@then(parsers.parse('the response body should contain "{text}"'))
def check_response_contains(text):
    assert response['resp'] is not None
    logger.info(f"Asserting response contains text: '{text}'")
    assert text in response['resp'].text

@then("the ping response body must contain result or latency")
def check_result_or_latency():
    assert response['resp'] is not None, "No response received"
    data = response['resp'].json()
    logger.info("Checking if response contains 'result', 'latency', or 'output'")
    assert any(key in data for key in ['result', 'latency', 'output']), \
        "Expected one of 'result', 'latency', or 'output' in response"

@then("the ping destination IP should match the input destination IPexplain")
def validate_destination_ip_match():
    assert response['resp'] is not None, "No response received"
    assert response['resp'].status_code == 200, "API call did not succeed"
    try:
        response_json = response['resp'].json()
    except Exception:
        logger.error("Response is not valid JSON")
        pytest.fail("Response is not valid JSON")

    output_text = response_json.get("output", "")
    logger.info(f"Raw output text: {output_text}")
    match = re.search(r'PING\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', output_text)
    actual_dest = match.group(1) if match else None
    expected_dest = response.get("expected_destination")

    logger.info(f"Expected destination: {expected_dest}, Actual from output: {actual_dest}")
    assert actual_dest == expected_dest, (
        f"Destination IP mismatch: sent '{expected_dest}', received '{actual_dest}'"
    )






'''
import os
import re

import pytest
import requests
import logging
from pathlib import Path
from typing import Final
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers

# --- Logging Setup ---
# LOG_FILE = Path("/home/vboxuser/Documents/mcn-qa-pytest/api/cloud/steps/test_ping.log")



LOG_FILE: Final = Path(__file__).parent / "test_ping.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# --- Feature File Binding ---
scenarios('../run_test_ping.feature')

response = {}

@given("the query parameters are valid")
def valid_query_params(source_ip, destination_ip, ping_type):
    logger.info("Setting valid query parameters")
    response['params'] = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    response['expected_destination'] = destination_ip

@given(parsers.parse('the query parameters are missing "{param}"'))
def missing_query_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Removing query parameter: {param}")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    query.pop(param, None)
    response['params'] = query

@given(parsers.parse('the query parameters are invalid "{param}"'))
def invalid_query_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Making query parameter '{param}' invalid")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    if param == "destination":
        query["destination"] = "invalid_ip"
    response['params'] = query

@given(parsers.parse('the query parameters have special characters in "{param}"'))
def special_characters_in_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Inserting special characters in param: {param}")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    query[param] = "!@#type$%"
    response['params'] = query

@given("the request headers are valid")
def valid_headers(tenant_id):
    logger.info("Setting valid request headers")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }

@given(parsers.parse('the request headers are missing "{header}"'))
def missing_header(header, tenant_id):
    logger.info(f"Removing request header: {header}")
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    headers.pop(header, None)
    response['headers'] = headers

@given('the request headers contain "X-TenantID" with invalid value')
def invalid_x_tenantid():
    logger.info("Setting invalid X-TenantID header")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": "!!invalid##"
    }

@when("the API request is sent")
def send_request(ping_api_url):
    logger.info("Sending API request with params and headers")
    try:
        resp = requests.get(ping_api_url, headers=response.get('headers', {}), params=response.get('params', {}))
        response['resp'] = resp
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@when("I trigger ping metrics request using env config")
def ping_metrics_from_env(ping_api_url, source_ip, destination_ip, tenant_id, ping_type):
    logger.info("Triggering ping metrics request using dynamic source/destination IPs")
    params = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    try:
        resp = requests.get(ping_api_url, headers=headers, params=params)
        response['resp'] = resp
        response['expected_destination'] = destination_ip
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@then(parsers.parse('the response code should be {expected_code:d}'))
@then(parsers.parse('the ping metrics API response code should be {expected_code:d}'))
def check_status_code(expected_code):
    assert response['resp'] is not None, f"Request failed: {response.get('error')}"
    actual_code = response['resp'].status_code
    logger.info(f"Asserting status code: expected={expected_code}, actual={actual_code}")
    if actual_code != expected_code:
        logger.warning("Full response body: %s", response['resp'].text)
    assert actual_code == expected_code

@then(parsers.parse('the response body should contain "{text}"'))
def check_response_contains(text):
    assert response['resp'] is not None
    logger.info(f"Asserting response contains text: '{text}'")
    assert text in response['resp'].text

@then("the ping response body must contain result or latency")
def check_result_or_latency():
    assert response['resp'] is not None, "No response received"
    data = response['resp'].json()
    logger.info("Checking if response contains 'result', 'latency', or 'output'")
    assert any(key in data for key in ['result', 'latency', 'output']), \
        "Expected one of 'result', 'latency', or 'output' in response"

@then("the ping destination IP should match the input destination IPexplain")
def validate_destination_ip_match():
    assert response['resp'] is not None, "No response received"
    assert response['resp'].status_code == 200, "API call did not succeed"
    try:
        response_json = response['resp'].json()
    except Exception:
        logger.error("Response is not valid JSON")
        pytest.fail("Response is not valid JSON")

    output_text = response_json.get("output", "")
    logger.info(f"Raw output text: {output_text}")
    match = re.search(r'PING\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', output_text)
    actual_dest = match.group(1) if match else None
    expected_dest = response.get("expected_destination")

    logger.info(f"Expected destination: {expected_dest}, Actual from output: {actual_dest}")
    assert actual_dest == expected_dest, (
        f"Destination IP mismatch: sent '{expected_dest}', received '{actual_dest}'"
    )'''



# last working file

'''import os
import re
import pytest
import requests
import logging
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Feature file binding
scenarios('../run_test_ping.feature')

response = {}

@given("the query parameters are valid")
def valid_query_params(source_ip, destination_ip, ping_type):
    logger.info("Setting valid query parameters")
    response['params'] = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    response['expected_destination'] = destination_ip

@given(parsers.parse('the query parameters are missing "{param}"'))
def missing_query_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Removing query parameter: {param}")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    query.pop(param, None)
    response['params'] = query

@given(parsers.parse('the query parameters are invalid "{param}"'))
def invalid_query_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Making query parameter '{param}' invalid")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    if param == "destination":
        query["destination"] = "invalid_ip"
    response['params'] = query

@given(parsers.parse('the query parameters have special characters in "{param}"'))
def special_characters_in_param(param, source_ip, destination_ip, ping_type):
    logger.info(f"Inserting special characters in param: {param}")
    query = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    query[param] = "!@#type$%"
    response['params'] = query

@given("the request headers are valid")
def valid_headers(tenant_id):
    logger.info("Setting valid request headers")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }

@given(parsers.parse('the request headers are missing "{header}"'))
def missing_header(header, tenant_id):
    logger.info(f"Removing request header: {header}")
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    headers.pop(header, None)
    response['headers'] = headers

@given('the request headers contain "X-TenantID" with invalid value')
def invalid_x_tenantid():
    logger.info("Setting invalid X-TenantID header")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": "!!invalid##"
    }

@when("the API request is sent")
def send_request(ping_api_url):
    logger.info("Sending API request with params and headers")
    try:
        resp = requests.get(ping_api_url, headers=response.get('headers', {}), params=response.get('params', {}))
        response['resp'] = resp
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@when("I trigger ping metrics request using env config")
def ping_metrics_from_env(ping_api_url, source_ip, destination_ip, tenant_id, ping_type):
    logger.info("Triggering ping metrics request using dynamic source/destination IPs")
    params = {
        "source": source_ip,
        "destination": destination_ip,
        "type": ping_type
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    try:
        resp = requests.get(ping_api_url, headers=headers, params=params)
        response['resp'] = resp
        response['expected_destination'] = destination_ip
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@then(parsers.parse('the response code should be {expected_code:d}'))
@then(parsers.parse('the ping metrics API response code should be {expected_code:d}'))
def check_status_code(expected_code):
    assert response['resp'] is not None, f"Request failed: {response.get('error')}"
    actual_code = response['resp'].status_code
    logger.info(f"Asserting status code: expected={expected_code}, actual={actual_code}")
    if actual_code != expected_code:
        logger.warning("Full response body: %s", response['resp'].text)
    assert actual_code == expected_code

@then(parsers.parse('the response body should contain "{text}"'))
def check_response_contains(text):
    assert response['resp'] is not None
    logger.info(f"Asserting response contains text: '{text}'")
    assert text in response['resp'].text

@then("the ping response body must contain result or latency")
def check_result_or_latency():
    assert response['resp'] is not None, "No response received"
    data = response['resp'].json()
    logger.info("Checking if response contains 'result', 'latency', or 'output'")
    assert any(key in data for key in ['result', 'latency', 'output']), \
        "Expected one of 'result', 'latency', or 'output' in response"

@then("the ping destination IP should match the input destination IPexplain")
def validate_destination_ip_match():
    assert response['resp'] is not None, "No response received"
    assert response['resp'].status_code == 200, "API call did not succeed"
    try:
        response_json = response['resp'].json()
    except Exception:
        logger.error("Response is not valid JSON")
        pytest.fail("Response is not valid JSON")

    output_text = response_json.get("output", "")
    logger.info(f"Raw output text: {output_text}")
    match = re.search(r'PING\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', output_text)
    actual_dest = match.group(1) if match else None
    expected_dest = response.get("expected_destination")

    logger.info(f"Expected destination: {expected_dest}, Actual from output: {actual_dest}")
    assert actual_dest == expected_dest, (
        f"Destination IP mismatch: sent '{expected_dest}', received '{actual_dest}'"
    )'''



# working fine 29.07.2025
'''
import os
import re
import pytest
import requests
import logging
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load .env values
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../env/qa.env'))
DEFAULT_SOURCE = os.getenv("PING_SOURCE_IP")
DEFAULT_DESTINATION = os.getenv("PING_DESTINATION_IP")
DEFAULT_TENANT = os.getenv("PING_TENANT_ID")
DEFAULT_TYPE = os.getenv("PING_TYPE")

# Feature file binding
scenarios('../run_test_ping.feature')

response = {}

@given("the query parameters are valid")
def valid_query_params():
    logger.info("Setting valid query parameters")
    response['params'] = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    response['expected_destination'] = DEFAULT_DESTINATION

@given(parsers.parse('the query parameters are missing "{param}"'))
def missing_query_param(param):
    logger.info(f"Removing query parameter: {param}")
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    query.pop(param, None)
    response['params'] = query

@given(parsers.parse('the query parameters are invalid "{param}"'))
def invalid_query_param(param):
    logger.info(f"Making query parameter '{param}' invalid")
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    if param == "destination":
        query["destination"] = "invalid_ip"
    response['params'] = query

@given(parsers.parse('the query parameters have special characters in "{param}"'))
def special_characters_in_param(param):
    logger.info(f"Inserting special characters in param: {param}")
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    query[param] = "!@#type$%"
    response['params'] = query

@given("the request headers are valid")
def valid_headers():
    logger.info("Setting valid request headers")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }

@given(parsers.parse('the request headers are missing "{header}"'))
def missing_header(header):
    logger.info(f"Removing request header: {header}")
    headers = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }
    headers.pop(header, None)
    response['headers'] = headers

@given('the request headers contain "X-TenantID" with invalid value')
def invalid_x_tenantid():
    logger.info("Setting invalid X-TenantID header")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": "!!invalid##"
    }

@when("the API request is sent")
def send_request(ping_api_url):
    logger.info("Sending API request with params and headers")
    try:
        resp = requests.get(ping_api_url, headers=response.get('headers', {}), params=response.get('params', {}))
        response['resp'] = resp
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@when("I trigger ping metrics request using env config")
def ping_metrics_from_env(ping_api_url):
    logger.info("Triggering ping metrics request using env config")
    params = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }
    try:
        resp = requests.get(ping_api_url, headers=headers, params=params)
        response['resp'] = resp
        response['expected_destination'] = DEFAULT_DESTINATION
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@then(parsers.parse('the response code should be {expected_code:d}'))
@then(parsers.parse('the ping metrics API response code should be {expected_code:d}'))
def check_status_code(expected_code):
    assert response['resp'] is not None, f"Request failed: {response.get('error')}"
    actual_code = response['resp'].status_code
    logger.info(f"Asserting status code: expected={expected_code}, actual={actual_code}")
    if actual_code != expected_code:
        logger.warning("Full response body: %s", response['resp'].text)
    assert actual_code == expected_code

@then(parsers.parse('the response body should contain "{text}"'))
def check_response_contains(text):
    assert response['resp'] is not None
    logger.info(f"Asserting response contains text: '{text}'")
    assert text in response['resp'].text

@then("the ping response body must contain result or latency")
def check_result_or_latency():
    assert response['resp'] is not None, "No response received"
    data = response['resp'].json()
    logger.info("Checking if response contains 'result', 'latency', or 'output'")
    assert any(key in data for key in ['result', 'latency', 'output']), \
        "Expected one of 'result', 'latency', or 'output' in response"

@then("the ping destination IP should match the input destination IPexplain")
def validate_destination_ip_match():
    assert response['resp'] is not None, "No response received"
    assert response['resp'].status_code == 200, "API call did not succeed"
    try:
        response_json = response['resp'].json()
    except Exception:
        logger.error("Response is not valid JSON")
        pytest.fail("Response is not valid JSON")

    output_text = response_json.get("output", "")
    logger.info(f"Raw output text: {output_text}")
    match = re.search(r'PING\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', output_text)
    actual_dest = match.group(1) if match else None
    expected_dest = response.get("expected_destination")

    logger.info(f"Expected destination: {expected_dest}, Actual from output: {actual_dest}")
    assert actual_dest == expected_dest, (
        f"Destination IP mismatch: sent '{expected_dest}', received '{actual_dest}'"
    )
'''





'''import os
import re
import pytest
import requests
import logging
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../env/qa.env'))

BASE_URL = os.getenv("PING_API_URL", "http://localhost:8080/metrics/diagnose")
DEFAULT_SOURCE = os.getenv("PING_SOURCE_IP")
DEFAULT_DESTINATION = os.getenv("PING_DESTINATION_IP")
DEFAULT_TENANT = os.getenv("PING_TENANT_ID")
DEFAULT_TYPE = os.getenv("PING_TYPE")

scenarios('../run_test_ping.feature')

response = {}

@given("the query parameters are valid")
def valid_query_params():
    logger.info("Setting valid query parameters")
    response['params'] = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    response['expected_destination'] = DEFAULT_DESTINATION

@given(parsers.parse('the query parameters are missing "{param}"'))
def missing_query_param(param):
    logger.info(f"Removing query parameter: {param}")
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    query.pop(param, None)
    response['params'] = query

@given(parsers.parse('the query parameters are invalid "{param}"'))
def invalid_query_param(param):
    logger.info(f"Making query parameter '{param}' invalid")
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    if param == "destination":
        query["destination"] = "invalid_ip"
    response['params'] = query

@given(parsers.parse('the query parameters have special characters in "{param}"'))
def special_characters_in_param(param):
    logger.info(f"Inserting special characters in param: {param}")
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    query[param] = "!@#type$%"
    response['params'] = query

@given("the request headers are valid")
def valid_headers():
    logger.info("Setting valid request headers")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }

@given(parsers.parse('the request headers are missing "{header}"'))
def missing_header(header):
    logger.info(f"Removing request header: {header}")
    headers = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }
    headers.pop(header, None)
    response['headers'] = headers

@given('the request headers contain "X-TenantID" with invalid value')
def invalid_x_tenantid():
    logger.info("Setting invalid X-TenantID header")
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": "!!invalid##"
    }

@when("the API request is sent")
def send_request():
    logger.info("Sending API request with params and headers")
    try:
        resp = requests.get(BASE_URL, headers=response.get('headers', {}), params=response.get('params', {}))
        response['resp'] = resp
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@when("I trigger ping metrics request using env config")
def ping_metrics_from_env():
    logger.info("Triggering ping metrics request using env config")
    params = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }
    try:
        resp = requests.get(BASE_URL, headers=headers, params=params)
        response['resp'] = resp
        response['expected_destination'] = DEFAULT_DESTINATION
        logger.info(f"Received response with status code: {resp.status_code}")
    except Exception as e:
        logger.error(f"Request failed: {e}")
        response['resp'] = None
        response['error'] = str(e)

@then(parsers.parse('the response code should be {expected_code:d}'))
@then(parsers.parse('the ping metrics API response code should be {expected_code:d}'))
def check_status_code(expected_code):
    assert response['resp'] is not None, f"Request failed: {response.get('error')}"
    actual_code = response['resp'].status_code
    logger.info(f"Asserting status code: expected={expected_code}, actual={actual_code}")
    if actual_code != expected_code:
        logger.warning("Full response body: %s", response['resp'].text)
    assert actual_code == expected_code

@then(parsers.parse('the response body should contain "{text}"'))
def check_response_contains(text):
    assert response['resp'] is not None
    logger.info(f"Asserting response contains text: '{text}'")
    assert text in response['resp'].text

@then("the ping response body must contain result or latency")
def check_result_or_latency():
    assert response['resp'] is not None, "No response received"
    data = response['resp'].json()
    logger.info("Checking if response contains 'result', 'latency', or 'output'")
    assert any(key in data for key in ['result', 'latency', 'output']), \
        "Expected one of 'result', 'latency', or 'output' in response"

@then("the ping destination IP should match the input destination IPexplain")
def validate_destination_ip_match():
    assert response['resp'] is not None, "No response received"
    assert response['resp'].status_code == 200, "API call did not succeed"
    try:
        response_json = response['resp'].json()
    except Exception:
        logger.error("Response is not valid JSON")
        pytest.fail("Response is not valid JSON")

    output_text = response_json.get("output", "")
    logger.info(f"Raw output text: {output_text}")
    match = re.search(r'PING\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', output_text)
    actual_dest = match.group(1) if match else None
    expected_dest = response.get("expected_destination")

    logger.info(f"Expected destination: {expected_dest}, Actual from output: {actual_dest}")
    assert actual_dest == expected_dest, (
        f"Destination IP mismatch: sent '{expected_dest}', received '{actual_dest}'"
    )'''





'''import os
import re
import pytest
import requests
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../env/qa.env'))

BASE_URL = os.getenv("PING_API_URL", "http://localhost:8080/metrics/diagnose")
DEFAULT_SOURCE = os.getenv("PING_SOURCE_IP")
DEFAULT_DESTINATION = os.getenv("PING_DESTINATION_IP")
DEFAULT_TENANT = os.getenv("PING_TENANT_ID")
DEFAULT_TYPE = os.getenv("PING_TYPE")

scenarios('../run_test_ping.feature')

response = {}

@given("the query parameters are valid")
def valid_query_params():
    response['params'] = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    response['expected_destination'] = DEFAULT_DESTINATION

@given(parsers.parse('the query parameters are missing "{param}"'))
def missing_query_param(param):
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    query.pop(param, None)
    response['params'] = query

@given(parsers.parse('the query parameters are invalid "{param}"'))
def invalid_query_param(param):
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    if param == "destination":
        query["destination"] = "invalid_ip"
    response['params'] = query

@given(parsers.parse('the query parameters have special characters in "{param}"'))
def special_characters_in_param(param):
    query = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    query[param] = "!@#type$%"
    response['params'] = query

@given("the request headers are valid")
def valid_headers():
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }

@given(parsers.parse('the request headers are missing "{header}"'))
def missing_header(header):
    headers = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }
    headers.pop(header, None)
    response['headers'] = headers

@given('the request headers contain "X-TenantID" with invalid value')
def invalid_x_tenantid():
    response['headers'] = {
        "accept": "*/*",
        "X-TenantID": "!!invalid##"
    }



@when("the API request is sent")
def send_request():
    try:
        resp = requests.get(BASE_URL, headers=response.get('headers', {}), params=response.get('params', {}))
        response['resp'] = resp
    except Exception as e:
        response['resp'] = None
        response['error'] = str(e)

@when("I trigger ping metrics request using env config")
def ping_metrics_from_env():
    params = {
        "source": DEFAULT_SOURCE,
        "destination": DEFAULT_DESTINATION,
        "type": DEFAULT_TYPE
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": DEFAULT_TENANT
    }
    try:
        resp = requests.get(BASE_URL, headers=headers, params=params)
        response['resp'] = resp
        response['expected_destination'] = DEFAULT_DESTINATION
    except Exception as e:
        response['resp'] = None
        response['error'] = str(e)


@then(parsers.parse('the response code should be {expected_code:d}'))
@then(parsers.parse('the ping metrics API response code should be {expected_code:d}'))
def check_status_code(expected_code):
    assert response['resp'] is not None, f"Request failed: {response.get('error')}"
    if response['resp'].status_code != expected_code:
        print("Response status:", response['resp'].status_code)
        print("Response body:", response['resp'].text)
    assert response['resp'].status_code == expected_code

@then(parsers.parse('the response body should contain "{text}"'))
def check_response_contains(text):
    assert response['resp'] is not None
    assert text in response['resp'].text

@then("the ping response body must contain result or latency")
def check_result_or_latency():
    assert response['resp'] is not None, "No response received"
    data = response['resp'].json()
    assert any(key in data for key in ['result', 'latency', 'output']), \
        "Expected one of 'result', 'latency', or 'output' in response"
    


@then("the ping destination IP should match the input destination IPexplain")
def validate_destination_ip_match():
    assert response['resp'] is not None, "No response received"
    assert response['resp'].status_code == 200, "API call did not succeed"
    try:
        response_json = response['resp'].json()
    except Exception:
        pytest.fail("Response is not valid JSON")

    output_text = response_json.get("output", "")
    match = re.search(r'PING\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', output_text)
    actual_dest = match.group(1) if match else None
    expected_dest = response.get("expected_destination")

    assert actual_dest == expected_dest, (
        f"Destination IP mismatch: sent '{expected_dest}', received '{actual_dest}'"
    )
'''