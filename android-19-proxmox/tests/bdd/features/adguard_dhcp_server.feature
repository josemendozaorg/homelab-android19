@acceptance @bdd @adguard @dhcp @network
Feature: AdGuard Home DHCP Server for Network-Wide DNS
  As a homelab administrator
  I want to enable AdGuard Home's built-in DHCP server
  So that all network devices automatically use AdGuard DNS and can resolve .homelab domains

  Background:
    Given the Proxmox host "192.168.0.19" is accessible
    And the AdGuard Home container 125 exists and is running
    And the infrastructure catalog defines network configuration

  @configuration @dhcp_enabled_configured
  Scenario: DHCP Configuration Enabled (Router DHCP Disabled)
    Given the AdGuard Ansible role has default configuration
    When the configuration is loaded
    Then the DHCP enabled flag should be "true"
    And the DHCP configuration variables should exist
    And the DHCP range should be "192.168.0.200" to "192.168.0.249"
    And the DHCP gateway should reference catalog network gateway
    And the DHCP subnet mask should be "255.255.255.0"
    And the DHCP lease duration should be "86400" seconds

  @deployment @dhcp_enabled_active
  Scenario: Deploy AdGuard with DHCP Enabled (Active Configuration)
    Given router DHCP has been disabled
    And DHCP is enabled in Ansible configuration
    When the administrator deploys AdGuard configuration
    Then the AdGuard configuration file should contain DHCP settings
    And DHCP enabled should be set to true
    And the AdGuard service should be running

  @deployment @dhcp_enabled @network_critical
  Scenario: Deploy AdGuard with DHCP Enabled
    Given router DHCP has been disabled
    And DHCP is enabled in Ansible configuration
    When the administrator deploys AdGuard configuration
    Then the AdGuard configuration file should contain DHCP settings
    And DHCP enabled should be set to true
    And DHCP interface should be "eth0"
    And DHCP IPv4 gateway should be "192.168.0.1"
    And DHCP IPv4 range should be "192.168.0.200" to "192.168.0.249"
    And DHCP IPv4 subnet mask should be "255.255.255.0"
    And DHCP IPv4 lease duration should be 86400 seconds
    And the AdGuard service should restart successfully

  @validation @template_rendering
  Scenario: DHCP Template Renders Correctly
    Given the AdGuard configuration template exists
    When the template is rendered with DHCP enabled
    Then the rendered configuration should be valid YAML
    And the DHCP section should use all configured variables
    And no variables should be undefined or null

  @safety @ip_conflict_prevention
  Scenario: DHCP Range Does Not Conflict with Static IPs
    Given the network strategy defines static IP ranges
    And the DHCP configuration defines dynamic IP range
    When the IP ranges are compared
    Then DHCP range should start at or after IP .200
    And DHCP range should end at or before IP .249
    And DHCP range should not overlap with container range (.20-.99)
    And DHCP range should not overlap with VM range (.100-.199)
    And DHCP range should not overlap with infrastructure range (.1-.19)

  @integration @dns_resolution_preparation
  Scenario: AdGuard DNS Rewrites Work with DHCP Configuration
    Given AdGuard has DNS rewrites configured for .homelab domains
    And DHCP is configured to advertise AdGuard as DNS server
    When DHCP clients receive network configuration
    Then clients should receive DNS server "192.168.0.25"
    And clients should receive gateway "192.168.0.1"
    And clients should be able to resolve "coolify.homelab" to "192.168.0.160"
    And clients should be able to resolve "ollama.homelab" to "192.168.0.140"
    And clients should be able to resolve "proxmox.homelab" to "192.168.0.19"
