# ADR-002: Homelab Network Strategy

## Status
Proposed

## Context
The homelab needs a network architecture that balances simplicity, security, and functionality for hosting applications across multiple environments (development, staging, production) and infrastructure services. Research into 2024/2025 homelab best practices reveals several viable approaches with different trade-offs.

## Research Summary

### Flat Network Approach
- **Pros**: Simplest setup, minimal configuration, better performance, works with basic equipment
- **Cons**: No security boundaries, all devices can access everything, single failure domain
- **Best for**: Small homelabs, learning environments, when simplicity is paramount

### VLAN Segmentation
- **Pros**: Strong security boundaries, logical separation, industry standard
- **Cons**: Complex configuration, requires managed switches, expensive hardware, can be over-engineered
- **Best for**: Production environments, compliance requirements, large homelabs

### Hybrid Container/VM Networking
- **Pros**: Leverages built-in container networking, simpler than VLANs, good security
- **Cons**: Limited to containerized workloads, requires orchestration platform
- **Best for**: Cloud-native applications, Kubernetes environments

## Decision

### Progressive Network Strategy

Implement a **progressive three-phase approach** that starts simple and adds complexity only when needed:

#### Phase 1: Enhanced Flat Network (Current - Start Here)
Use single subnet with logical IP organization and application-level security.

**Network**: 192.168.0.0/24
- `.1-9` - Router/gateway infrastructure
- `.10-19` - Physical hosts (bastion .10, proxmox .19)
- `.20-99` - Container services (by category)
- `.100-199` - Virtual machines
- `.200-249` - DHCP pool for devices

**Security Strategy**:
- Application-level authentication (strong passwords, API keys)
- Firewall rules on individual services
- Container networking isolation where applicable
- Regular security updates and monitoring

**Benefits**:
- Works with existing consumer router
- No managed switch required
- Simple troubleshooting
- Easy service discovery
- Fast implementation

#### Phase 2: Container-Native Segmentation (When Running Multiple Applications)
Use container orchestration networking (Docker networks, Kubernetes network policies) for application isolation.

**Implementation**:
- Docker Compose networks for service stacks
- Kubernetes network policies for pod-to-pod communication
- Proxmox bridges for VM isolation
- Application-specific network namespaces

**Benefits**:
- No additional hardware required
- Leverages existing container security
- Application-aware networking
- Easier to manage than VLANs

#### Phase 3: VLAN Segmentation (When Security Requirements Increase)
Implement VLANs only when dealing with:
- Sensitive data requiring compliance
- IoT devices from untrusted vendors
- Guest access requirements
- Production workloads requiring isolation

**Minimal VLAN Design**:
- VLAN 1: Management + Core Services (DNS, monitoring)
- VLAN 10: Production Applications
- VLAN 20: Development/Testing
- VLAN 30: IoT/Untrusted Devices
- VLAN 40: Guest Network

## Current Implementation (Phase 1)

### IP Assignment Strategy
- **Container ID = IP Last Octet**: Easy mental mapping (ID 125 → IP .25)
- **Service Categories**: Group by function for logical organization
- **Static IPs**: All services use static assignment for reliability

### Current Services
```yaml
# Only services with Ansible implementations
services:
  125:
    name: "adguard"
    type: "container"
    ip: "192.168.0.25"
    category: "infrastructure"
```

### Security Measures
- AdGuard DNS filtering at network level
- SSH key authentication for all hosts
- Application-specific firewalls (iptables/nftables)
- Regular security updates via Ansible
- Strong authentication for all services

## Migration Criteria

### Move to Phase 2 When:
- Running 5+ different application stacks
- Need to isolate development from production
- Container orchestration is already in use
- Application dependencies become complex

### Move to Phase 3 When:
- Handling sensitive/regulated data
- Need to support guest access
- Running IoT devices from untrusted vendors
- Security audit requirements
- Network performance issues from broadcast traffic

## Benefits of Progressive Approach

### Immediate Benefits (Phase 1)
- Start immediately with existing equipment
- Learn networking fundamentals without complexity
- Focus on application development and automation
- Easy troubleshooting and maintenance

### Long-term Benefits
- Natural growth path as needs evolve
- Each phase builds on previous knowledge
- Can stop at any phase that meets requirements
- Avoids over-engineering from the start

### Cost Benefits
- No upfront investment in managed switches
- Upgrade hardware only when needed
- Learn what features are actually required
- Avoid buying equipment that won't be used

## Implementation Guidelines

### Phase 1 Rules
1. All services use static IP assignments from catalog
2. IP ranges are reserved by service type for organization
3. Container/VM IDs match IP last octet when possible
4. Application-level security is mandatory
5. Regular automated security updates

### Documentation Requirements
- Infrastructure catalog tracks all services and IPs
- Network diagram shows current topology
- Security measures documented per service
- Migration triggers clearly defined

### Monitoring and Review
- Quarterly review of network performance
- Annual security assessment
- Evaluate migration criteria every 6 months
- Document lessons learned from each phase

## Consequences

### Positive
- Starts simple and grows with needs
- Lower barrier to entry
- Natural learning progression
- Cost-effective approach
- Avoids premature optimization

### Negative
- Security relies more on application-level controls
- May need to refactor networking later
- Some advanced features require eventual migration
- Requires discipline to maintain IP organization

### Mitigation
- Strong application security from day one
- Plan migration paths from the beginning
- Regular security reviews and updates
- Clear documentation of current state

## Alternatives Considered

1. **Immediate VLAN Implementation**: Rejected due to complexity and cost for single-user homelab
2. **Cloud-First Architecture**: Rejected due to ongoing costs and loss of learning opportunities
3. **Multiple Physical Networks**: Rejected due to equipment costs and complexity
4. **Software-Defined Networking**: Deferred to Phase 2/3 based on actual needs

## References
- [Best Home Lab Networking Architecture 2025](https://www.virtualizationhowto.com/2025/01/best-home-lab-networking-architecture-in-2025/)
- [Homelab Network Design Guide](https://edywerder.ch/homelab-network/)
- [VLANs for Homelab Beginners](https://liore.com/vlans-for-the-homelab-a-beginners-guide-to-segmenting-networks/)
- [Flat Network vs VLAN Security](https://www.networkcomputing.com/network-infrastructure/how-to-secure-your-flat-network)