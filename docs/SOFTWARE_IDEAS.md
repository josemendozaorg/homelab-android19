# Proxmox Software Installation Ideas

This document contains software ideas to consider for installation on the Android #19 Proxmox server. These are ideas and inspirations, not definitive installation instructions.

## Core Infrastructure

### Virtualization & Management
- **ProxMox** → VM manager (already installed)
- **Packer** → [Proxmox VMs templates as code](https://www.virtualizationhowto.com/2025/07/5-proxmox-projects-to-level-up-your-home-lab-this-weekend/)
- **Proxmox Backup Server** → [Scheduled Proxmox backups](https://www.virtualizationhowto.com/2025/07/5-proxmox-projects-to-level-up-your-home-lab-this-weekend/)
- **Cloud-init** → Initialize new VMs with initial config (user, IP, SSH keys)
- **Firecracker** → microVMs for lightweight workloads

### Monitoring & Observability
- **Prometheus, InfluxDB, Grafana** → [Proxmox cluster monitoring](https://www.virtualizationhowto.com/2025/07/5-proxmox-projects-to-level-up-your-home-lab-this-weekend/)
- **Jaeger** → Telemetry and distributed tracing
- **NUT** → Network UPS Tools

## Networking & Security

### Network Infrastructure
- **OpenSense, pfSense LXC** → Firewall and Networking
- **Adguard LXC** → DNS filtering
- **Wireguard LXC** → VPN server
- **Traefik** → Load balancing and reverse-proxy
- **Cilium and Tetragon** → K8s security

### Authentication
- **Authentik SSO** → Single Sign-On for all homelab applications

## Storage & Data

### Storage Solutions
- **TrueNAS on Ubuntu VM** → Backups, dumps, media storage (with PCIe disk passthrough)
- **ZFS pools** → Direct Proxmox storage on NVMe cards for VM live disk space
- **S3-alike in K8s** → Object storage
- **HDFS in K8s** → File storage for parallel Spark processing

### File Management
- **Syncthing** → File sync between devices (Google Drive replacement)
- **Nextcloud** → Cloud storage and collaboration
- **Paperless-ngx** → Document storage and search

## Container & Kubernetes Management

### Container Platforms
- **Portainer, Tipi** → Container management
- **CasaOS or Coolify** → Platform as a Service
- **Runtipi** → One-click application installation as LXC containers

### Kubernetes Distributions
- **Talos Kubernetes** → Secure, minimal Kubernetes in VMs/LXC
- **Rancher or OKD Kubernetes** → Container orchestration (OpenShift)
- **KubeSphere** → [Distributed operating system for cloud-native apps](https://kubesphere.io/docs/v4.1/02-quickstart/01-install-kubesphere/)

### Kubernetes Tools
- **Fleet** → GitOps continuous deployment, Helm charts
- **Harbor** → Container and Helm chart registry
- **Tekton CD, ArgoCD, Helm** → Cloud-native CI/CD

## Databases

### SQL Databases
- **PostgreSQL in K8s** → Structured data storage

### NoSQL & Caching
- **Redis in K8s** → Key-value cache and JSON documents

## Development & CI/CD

### Development Tools
- **Git** → Code versioning
- **VS Code** → General IDE
- **IntelliJ** → Java IDE
- **Storybook** → UI component testing

### CI/CD Platforms
- **Jenkins** → Traditional CI/CD
- **Dagger** → Modern CI/CD pipelines
- **Evergreen, Agola** → Alternative CI/CD solutions

### Code Quality & Testing
- **Cypress** → End-to-end UI testing

## AI & Machine Learning

### LLM Inference
- **Ollama** → Local LLM server
- **LocalAI** → Drop-in replacement for OpenAI/Anthropic APIs
- **NimNodes** → NVIDIA LLM services for image generation

### AI Frameworks
- **LangGraph, CrewAI, AutoGen** → Agentic AI frameworks
- **KubeFlow** → AI/ML pipelines in Kubernetes
- **LoRA** → Fine-tuned LLM model adapters
- **EXO** → Distributed LLM inference across devices

### ML Operations
- **MLflow, Weights and Biases** → Experiment tracking
- **AutoML, Hyperopt** → Automated hyperparameter optimization
- **SHAP, Fairlearn, LIME** → Model explainability and fairness
- **BentoML, KServe** → Model serving
- **Data Version Control, Pachyderm** → Dataset versioning

## Media & Personal Services

### Photo Management
- **Immich** → Google Photos replacement
- **PhotoPrism** → Alternative photo management

### Home Automation
- **Zigbee server** → IoT device management
- **Frigate** → AI object detection for IP cameras

### 3D Printing
- **3D Printer remote manager**
- **Blender** → 3D modeling
- **Ultimaker Cura, PrusaSlicer** → 3D printing slicers

## Data Processing

### Stream Processing
- **Kafka, RabbitMQ** → Message queuing and topic servers
- **Spark Cluster in K8s** → Data transformation pipelines

### Serverless
- **Fission, Knative, OpenWhisk** → Event-driven serverless functions

## Workflow & Automation

### Workflow Tools
- **n8n server** → Low-code workflows

## Remote Access

### Remote Management
- **PiKVM** → Remote KVM and power control (IPMI alternative)
- **NoMachine** → Remote desktop for Ubuntu/Windows VMs
- **Remote Desktop Chrome** → Alternative RDP solution

## User Interface

### Dashboards
- **Homarr** → Home lab application dashboard (preferred)
- **Glace, Dashy** → Alternative dashboards

## Development Tools

### Specialized Tools
- **Claude Code** → AI-assisted programming
- **Claude Flow** → Swarm of parallel agents
- **E2B** → Secure AI code execution sandbox
- **Firecrawl** → Web crawler
- **OpenLovable** → Open source alternative to Lovable

### Shell Enhancement
- **Starship** → Enhanced shell prompt

## Hardware Control
- **SignalRGB** → RGB lighting control

---

## Notes

- This is a collection of ideas, not a definitive installation plan
- Consider resource requirements and dependencies when selecting software
- Some tools overlap in functionality - choose based on specific needs
- Start with core infrastructure and gradually add specialized tools
- Test in development VMs before production deployment