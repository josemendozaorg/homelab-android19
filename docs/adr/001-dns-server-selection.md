# ADR-001: DNS Server Selection for Homelab

## Status
**ACCEPTED** - 2025-09-21

## Context

The homelab requires a DNS server to enable hostname-based service discovery instead of relying on IP addresses. This is essential for:

- Accessing homelab services by name (e.g., `pve.lab`, `android16.lab`)
- Simplifying service configuration and management
- Providing ad-blocking and privacy protection network-wide
- Supporting future service deployments with meaningful hostnames

The DNS server will run in an LXC container on the Android #19 Proxmox server and serve the entire 192.168.0.0/24 network.

## Decision

**We will use AdGuard Home as the DNS server solution.**

## Rationale

### Considered Alternatives

1. **AdGuard Home** - Modern DNS server with ad-blocking
2. **Pi-hole** - Established DNS server with ad-blocking
3. **Bind9** - Traditional DNS server (no built-in ad-blocking)

### Evaluation Criteria

- Resource efficiency (important for LXC containers)
- Ease of custom DNS record management
- Built-in security features (DoH/DoT)
- Management interface quality
- Performance characteristics
- Maintenance overhead

### Why AdGuard Home

**Advantages:**
- **Resource Efficient**: ~50-100MB RAM vs Pi-hole's ~100-200MB
- **Modern Architecture**: Single Go binary, no dependencies
- **Built-in Encrypted DNS**: DoH/DoT support without additional configuration
- **Easy Custom DNS Management**: Web UI for adding homelab service records
- **Better Performance**: Generally faster query resolution
- **Modern Web Interface**: Responsive design, better mobile support
- **Active Development**: Frequent updates and new features

**Trade-offs Accepted:**
- Smaller community compared to Pi-hole
- Less extensive plugin ecosystem
- Newer solution with shorter track record

### Why Not Pi-hole

While Pi-hole is more mature with larger community support, it requires:
- Higher resource usage
- Manual file editing for custom DNS records
- Additional setup for encrypted DNS
- PHP dependencies and more complex architecture

### Why Not Bind9

Bind9 lacks built-in ad-blocking and would require additional tools, increasing complexity and resource usage.

## Consequences

### Positive
- Lower resource usage in LXC container environment
- Easier management of homelab service DNS records
- Built-in privacy protection (ad-blocking + encrypted upstream DNS)
- Modern, responsive management interface
- Simple backup/restore (single binary + config file)

### Negative
- Smaller community for troubleshooting complex issues
- Less extensive third-party integration ecosystem
- Team needs to learn AdGuard-specific configuration

### Neutral
- One-time migration effort if switching from other DNS solutions
- Regular maintenance for blocklist updates (automated)

## Implementation Plan

1. Create Ubuntu 22.04 LXC container in Proxmox
2. Install AdGuard Home via official installer
3. Configure initial DNS records for homelab services
4. Set up encrypted upstream DNS (Cloudflare DoH)
5. Create Ansible playbook for automated deployment
6. Update network DHCP to use AdGuard as primary DNS
7. Test and validate DNS resolution and ad-blocking

## Success Metrics

- [ ] All homelab services accessible via `.lab` hostnames
- [ ] Ad-blocking operational (>90% blocked ads in statistics)
- [ ] DNS query response time <50ms for local records
- [ ] Zero DNS-related service interruptions
- [ ] Successful automated deployment via Ansible