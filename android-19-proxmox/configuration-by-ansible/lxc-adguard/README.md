# AdGuard Home Role

This role configures AdGuard Home as a comprehensive DNS solution for homelab environments, implementing industry best practices for security, privacy, and performance.

## Overview

The AdGuard Home role provides:
- **Privacy-focused DNS**: Uses Cloudflare (1.1.1.1) and Quad9 (9.9.9.9) as primary upstream servers
- **Security filtering**: Blocks malware, tracking, and malicious domains using curated blocklists
- **Homelab integration**: Custom DNS rewrites for internal services (.homelab domains)
- **Performance optimization**: Caching and TTL settings optimized for homelab use

## Prerequisites

- Container must be provisioned by Terraform (ID: 125)
- Container must have network connectivity
- Proxmox API access for container management

## Configuration

### DNS Upstream Servers

The role configures multiple upstream DNS servers for reliability and security:

```yaml
adguard_upstream_dns:
  - "1.1.1.1"          # Cloudflare - Fast, privacy-focused
  - "1.0.0.1"          # Cloudflare secondary
  - "9.9.9.9"          # Quad9 - Blocks malicious domains
  - "149.112.112.112"  # Quad9 secondary
  - "8.8.8.8"          # Google DNS (fallback)
```

### Security Blocklists

Industry-standard filter lists are automatically configured:

- **AdGuard Base Filter**: Core ad and tracker blocking
- **AdGuard Mobile Ads Filter**: Mobile-specific ad blocking
- **Malware Domains**: Security-focused malware protection
- **Dan Pollock's hosts file**: Additional malware/ad blocking
- **EasyPrivacy**: Privacy protection and tracking prevention
- **AdGuard Tracking Protection**: Enhanced tracking protection

### Homelab DNS Rewrites

Custom domains for easy access to homelab services:

```yaml
adguard_dns_rewrites:
  - domain: "proxmox.homelab"
    ip: "192.168.0.19"
  - domain: "adguard.homelab"
    ip: "192.168.0.125"
  - domain: "bastion.homelab"
    ip: "192.168.0.16"
```

### Performance Settings

Optimized for homelab environments:

- **Cache Size**: 4MB for efficient query caching
- **Cache TTL**: 60 seconds minimum, 24 hours maximum
- **Blocked Response TTL**: 300 seconds
- **Query Logging**: 24-hour retention
- **Statistics**: 24-hour retention

## Usage

### Deploy AdGuard Home

```bash
# Deploy AdGuard service only
make proxmox-adguard

# Or deploy all services
make proxmox-services
```

### Access AdGuard Home

After deployment:
- **Web Interface**: http://192.168.0.125:3000
- **DNS Server**: 192.168.0.125:53
- **Admin Username**: admin
- **Admin Password**: homelab123

### Configure Network

Update your router/DHCP server to use AdGuard as primary DNS:
1. Set primary DNS to `192.168.0.125`
2. Set secondary DNS to `192.168.0.1` (router) as fallback

### Test DNS Resolution

```bash
# Test homelab domain resolution
nslookup proxmox.homelab 192.168.0.125

# Test external domain resolution
nslookup google.com 192.168.0.125

# Test blocking (should return blocked response)
nslookup doubleclick.net 192.168.0.125
```

## Advanced Configuration

### Custom Filtering Rules

The role includes homelab-optimized filtering rules:

```yaml
adguard_custom_filtering_rules:
  # Allow local network ranges
  - "@@||192.168.0.0/24^"
  - "@@||10.0.0.0/8^"
  - "@@||172.16.0.0/12^"

  # Block tracking
  - "||google-analytics.com^"
  - "||googletagmanager.com^"

  # Allow development services
  - "@@||github.com^"
  - "@@||docker.io^"
```

### DNS-over-HTTPS/TLS (Optional)

For enhanced privacy, secure DNS endpoints are pre-configured but disabled by default:

```yaml
adguard_upstream_dns_secure:
  - "https://cloudflare-dns.com/dns-query"
  - "https://dns.quad9.net/dns-query"
  - "tls://1.1.1.1"
  - "tls://9.9.9.9"
```

### Parental Controls

Family-friendly options (disabled by default):

```yaml
adguard_parental_enabled: false    # Set to true for family filtering
adguard_safesearch_enabled: false  # Set to true for safe search
```

## Monitoring

### Query Logs

Monitor DNS queries and blocked requests:
- Access via web interface: **Query Log** section
- 24-hour retention by default
- Shows blocked vs allowed queries

### Statistics

View blocking effectiveness:
- **Dashboard**: Overview of queries and blocks
- **Query Types**: Distribution of DNS query types
- **Top Clients**: Most active devices
- **Top Blocked Domains**: Most blocked domains

### Performance Metrics

Monitor DNS performance:
- **Response Times**: Average query response time
- **Cache Hit Rate**: Percentage of queries served from cache
- **Upstream Usage**: Distribution across upstream servers

## Troubleshooting

### Common Issues

**DNS not resolving**:
```bash
# Check AdGuard service status
pct exec 125 -- systemctl status AdGuardHome

# Check network connectivity
pct exec 125 -- ping 8.8.8.8

# Check AdGuard configuration
curl http://192.168.0.125:3000/control/status
```

**Web interface not accessible**:
```bash
# Check if service is listening
pct exec 125 -- netstat -tlnp | grep 3000

# Check firewall
pct exec 125 -- iptables -L
```

**Blocked domains not working**:
- Wait for filter lists to update (up to 24 hours)
- Force refresh via web interface: **Filters** → **Update filters**
- Check filter list URLs are accessible

### Logs

View AdGuard logs:
```bash
pct exec 125 -- journalctl -u AdGuardHome -f
```

## Security Considerations

- Default admin credentials should be changed in production
- Consider enabling HTTPS for web interface
- Regular filter list updates ensure current threat protection
- Query logging may contain sensitive information - review retention policy

## Integration

### Router Configuration

For network-wide DNS filtering:
1. Configure router DHCP to advertise AdGuard as primary DNS
2. Disable router's DNS relay if present
3. Consider blocking port 53 outbound to prevent DNS bypass

### Backup Configuration

AdGuard configuration is stored in:
- `/opt/AdGuardHome/AdGuardHome.yaml` (main config)
- `/opt/AdGuardHome/data/` (statistics and logs)

Regular backups recommended for configuration persistence.