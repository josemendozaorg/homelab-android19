@acceptance @bdd @bastion @dns @network @safe
Feature: Bastion Host DNS Configuration
  As a homelab administrator
  I want the bastion host to use AdGuard DNS
  So that it can resolve .homelab domains and benefit from network-wide DNS filtering

  Background:
    Given the bastion host "192.168.0.10" is accessible
    And the infrastructure catalog defines network configuration
    And the AdGuard DNS server "192.168.0.25" is running

  @configuration @bastion_dns
  Scenario: Bastion DNS Configuration Uses Catalog
    Given the bastion Ansible playbook exists
    When the playbook configuration is loaded
    Then the playbook should load infrastructure catalog variables
    And DNS configuration should reference catalog network DNS
    And DNS server should be "192.168.0.25"
    And no DNS IP addresses should be hardcoded

  @deployment @bastion_dns @safe
  Scenario: Deploy Bastion with AdGuard DNS
    Given the bastion playbook includes DNS configuration tasks
    And DNS tasks are tagged with "dns"
    When the administrator deploys bastion DNS configuration
    Then the bastion should use DNS server "192.168.0.25"
    And DNS priority should be set to manual
    And the deployment should complete without errors

  @validation @dns_resolution @bastion_dns
  Scenario: Bastion Resolves Homelab Domains
    Given the bastion is configured to use AdGuard DNS
    When DNS is queried for homelab domains
    Then "proxmox.homelab" should resolve to "192.168.0.19"
    And "coolify.homelab" should resolve to "192.168.0.160"
    And "adguard.homelab" should resolve to "192.168.0.25"

  @validation @bastion_dns @safe
  Scenario: DNS Configuration is Idempotent
    Given the bastion is already configured with AdGuard DNS
    When the administrator re-deploys DNS configuration
    Then no changes should be made
    And the deployment should report "ok" or "changed=0"
    And DNS resolution should still work

  @safety @bastion_dns
  Scenario: DNS Configuration Uses NetworkManager
    Given the bastion playbook includes DNS configuration tasks
    When the DNS tasks are examined
    Then tasks should use nmcli commands
    And tasks should NOT use direct file editing of /etc/resolv.conf
    And tasks should set ignore-auto-dns to prevent DHCP override

  @integration @bastion_dns @safe
  Scenario: Bastion DNS Works with Static and DHCP Hosts
    Given the bastion is configured to use AdGuard DNS
    And the network has both static IP hosts and DHCP clients
    When DNS queries are made from bastion
    Then static IP hosts should be resolvable
    And DHCP clients should be resolvable
    And external domains should be resolvable
