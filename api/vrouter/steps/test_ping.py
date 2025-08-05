import os
import re
import pytest
import requests
import logging
from pathlib import Path
from typing import Final
from dotenv import load_dotenv
from pytest_bdd import scenarios, given, when, then, parsers


pytestmark = pytest.mark.ping



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

