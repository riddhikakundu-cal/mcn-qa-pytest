import requests
import logging
from pytest_bdd import scenarios, parsers, when, then


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


scenarios('../ping_metrics.feature')


response_data = {}

@when(parsers.cfparse("I ping metrics from {source} to {destination} with type {ping_type} for tenant {tenant_id}"))
def ping_metrics(source, destination, ping_type, tenant_id):
    url = "http://3.111.234.240:8080/metrics/diagnose"
    params = {
        "source": source,
        "destination": destination,
        "type": ping_type
    }
    headers = {
        "accept": "*/*",
        "X-TenantID": tenant_id
    }
    logger.info(f"Sending ping request: {url} with params: {params} and headers: {headers}")
    response = requests.get(url, params=params, headers=headers)
    response_data["response"] = response

@then(parsers.cfparse("the ping metrics API response code should be {status_code:d}"))
def validate_status_code(status_code):
    assert response_data["response"].status_code == status_code, \
        f"Expected {status_code}, got {response_data['response'].status_code}"

@then("the ping response body must contain diagnostic output")
def validate_response_body():
    json_data = response_data["response"].json()
    assert "output" in json_data, f"Response does not contain 'output'. Got: {json_data}"


