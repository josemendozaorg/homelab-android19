# Feature backlog
[x] - What needs to be configure to use the DNS rewrites like coolify.homelab? I put it in the browser and it does not work. Should the Proxmox DNS be configured to point to the Adguard DNS?
  **RESOLVED**: Implemented AdGuard Home DHCP server to provide network-wide DNS configuration.
  - See: `specs/adguard-dhcp-server/spec.md` for full specification
  - AdGuard DHCP server replaces router DHCP, automatically advertises itself as DNS to all clients
  - DHCP range: 192.168.0.200-249 (per ADR-002 network strategy)
  - Feature flag: `adguard_dhcp_enabled: false` (disabled by default for safety)
  - Deployment: Set `adguard_dhcp_enabled: true` + disable router DHCP + run `make deploy-lxc-adguard-dns`
  - Once enabled, all DHCP clients automatically resolve `.homelab` domains (coolify.homelab, ollama.homelab, etc.)