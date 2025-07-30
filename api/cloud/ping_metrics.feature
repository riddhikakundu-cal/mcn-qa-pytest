Feature: Ping Diagnostics Metrics API

  Scenario: Successful ping between valid vrouters
    When I ping metrics from 20.204.182.1 to 3.111.234.240 with type ping for tenant tata
    Then the ping metrics API response code should be 200
    And the ping response body must contain diagnostic output


  Scenario: Ping with invalid source IP
    When I ping metrics from 1.2.3.4 to 3.111.234.240 with type ping for tenant tata
    Then the ping metrics API response code should be 400


