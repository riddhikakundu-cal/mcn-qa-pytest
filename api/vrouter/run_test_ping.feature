Feature: Run Diagnostics API

  Scenario Outline: Valid request with all parameters and dynamic type
    Given the query parameters are valid
    And the request headers are valid
    When the API request is sent
    Then the response code should be 200
    And the response body should contain "output"

    Examples:
      | ping_type |
      | ping      |
      | trace     |

  Scenario Outline: Missing query parameter "source" with dynamic type
    Given the query parameters are missing "source"
    And the request headers are valid
    When the API request is sent
    Then the response code should be 400

    Examples:
      | ping_type |
      | ping      |
      | trace     |

  Scenario Outline: Missing request header "X-TenantID" with dynamic type
    Given the query parameters are valid
    And the request headers are missing "X-TenantID"
    When the API request is sent
    Then the response code should be 400

    Examples:
      | ping_type |
      | ping      |
      | trace     |

  Scenario Outline: Invalid query parameter "destination" with dynamic type
    Given the query parameters are invalid "destination"
    And the request headers are valid
    When the API request is sent
    Then the response code should be 400

    Examples:
      | ping_type |
      | ping      |
      | trace     |

  Scenario Outline: Special characters in query parameter "type" with dynamic type
    Given the query parameters have special characters in "type"
    And the request headers are valid
    When the API request is sent
    Then the response code should be 400

    Examples:
      | ping_type |
      | ping      |
      | trace     |

  Scenario Outline: Invalid request header "X-TenantID" with dynamic type
    Given the query parameters are valid
    And the request headers contain "X-TenantID" with invalid value
    When the API request is sent
    Then the response code should be 400

    Examples:
      | ping_type |
      | ping      |
      | trace     |

  Scenario Outline: Validate destination IP match in response with dynamic type
    When I trigger ping metrics request using env config
    Then the ping metrics API response code should be 200
    And the ping response body must contain result or latency
    And the ping destination IP should match the input destination IPexplain 

    Examples:
      | ping_type |
      | ping      |
      | trace     |
