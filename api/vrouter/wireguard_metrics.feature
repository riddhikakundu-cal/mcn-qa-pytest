Feature: WireGuard Metrics API
  As a system administrator
  I want to query WireGuard connection metrics
  So that I can monitor VPN connection status and performance

Background:
    Given the WireGuard metrics API is available

  Scenario: Query metrics with valid parameters
    Given valid source, peer, and time range parameters
    When I query wireguard connection status
    Then the metrics should be returned in the response



  Scenario: Query metrics with specific sourceVrouterID
    Given valid source, peer, and time range parameters
    When I query wireguard connection status
    Then the metrics should be returned 
    And the response must contain the sourceVrouterID provided



  Scenario: Query metrics with specific peerVrouterID
    Given valid source, peer, and time range parameters
    When I query wireguard connection status
    Then the metrics should be returned in the response
    And the response must contain the peerVrouterID provided


  Scenario: Query with invalid source vrouter ID
    Given invalid source source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with missing source vrouter ID
    Given no source source, peer, and time range parameters
    When I query wireguard connection status
    Then metrics for all vrouters should be returned

  Scenario: Query with invalid peer vrouter ID
    Given invalid peer source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with missing peer vrouter ID
    Given no peer source, peer, and time range parameters
    When I query wireguard connection status
    Then metrics for all peers should be returned

  Scenario: Query with invalid timeFrom parameter
    Given invalid timeFrom source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with missing timeFrom parameter
    Given no timeFrom source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with invalid timeTo parameter
    Given invalid timeTo source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with missing timeTo parameter
    Given no timeTo source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with incorrect timeTo format
    Given incorrect timeTo format source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query with timeTo entirely omitted
    Given timeTo is entirely omitted source, peer, and time range parameters
    When I query wireguard connection status
    Then the response should indicate failure or empty data

  Scenario: Query wireguard_tx_bytes metrics for a valid source and peer
    Given valid source, peer, and time range parameters
    When I query wireguard connection status with "wireguard_tx_bytes"
    Then the metrics should be returned in the response
    And the response contains non-empty values for tx_bytes
    And the values should be monotonically increasing
  
  Scenario: Query wireguard_rx_bytes metrics for a valid source and peer
    Given valid source, peer, and time range parameters
    When I query wireguard connection status with "wireguard_rx_bytes"
    Then the metrics should be returned in the response
    And the response contains non-empty values for rx_bytes

  Scenario: Query wireguard_tx_bytes with invalid peer
    Given valid source, invalid peer, and time range parameters
    When I query wireguard connection status with "wireguard_tx_bytes"
    Then the response should indicate failure or empty data

  Scenario: Query wireguard_rx_bytes with invalid time range
    Given valid source, peer, and invalid time range parameters
    When I query wireguard connection status with "wireguard_rx_bytes"
    Then the response should indicate failure or empty data

  Scenario: Query wireguard_rx_bytes for bytes increasing
    Given valid source, peer, and time range parameters
    When I query wireguard connection status with "wireguard_rx_bytes"
    Then the values should be monotonically increasing
