# 🚀 Omarchy VM Installation Guide

Choose your installation approach based on your preference for automation and control.

## 📋 Installation Approach Selection

### **Option 1: Fully Manual (Easiest)**
*Best for: First time users, those who want full control*

**Pros:**
- ✅ Official Omarchy experience
- ✅ Interactive disk setup with guidance
- ✅ No technical configuration needed
- ✅ Built-in error handling

**Cons:**
- ❌ Requires manual interaction
- ❌ Need to connect to VM console

**How to choose:** Use the default configuration (no changes needed)

---

### **Option 2: Semi-Automated (Recommended)**
*Best for: Experienced users who want faster deployment*

**Pros:**
- ✅ Faster installation
- ✅ Pre-configured disk encryption
- ✅ Automated base system setup
- ✅ Still use official Omarchy script

**Cons:**
- ❌ Requires archinstall knowledge
- ❌ More complex troubleshooting

**How to choose:** Set configuration flag in defaults

---

### **Option 3: Custom Automation (Advanced)**
*Best for: Developers who need completely hands-off deployment*

**Pros:**
- ✅ Completely headless (two-stage approach)
- ✅ Scriptable and repeatable
- ✅ No manual intervention required
- ✅ Uses official Omarchy script in Stage 2

**Cons:**
- ❌ Uses cloud-init approach (experimental)
- ❌ Requires Terraform support for QCOW2 import
- ❌ More complex troubleshooting if cloud-init fails

**How it works:**
1. **Cloud Image**: Uses official Arch Linux QCOW2 with cloud-init pre-installed
2. **Automation**: Cloud-init runs Omarchy script automatically on first boot
3. **Headless**: No manual console interaction required

**How to choose:** Use separate VM ID 102 with `make deploy-vm-omarchy-devmachine-automated`

---

## 🛠️ How to Choose Your Approach

### **Step 1: Configure Your Preference**

Edit the Omarchy VM defaults to choose your installation method:

```bash
# Edit configuration file
nano android-19-proxmox/configuration-by-ansible/vm-omarchy-dev/defaults/main.yml
```

Add one of these configurations:

```yaml
# OPTION 1: Fully Manual (Default)
omarchy_installation_method: "manual"
omarchy_guided_install: true

# OPTION 2: Semi-Automated
omarchy_installation_method: "semi-automated"
omarchy_use_archinstall_config: true
omarchy_automated_omarchy_script: true

# OPTION 3: Custom Automation (Experimental)
omarchy_installation_method: "custom"
omarchy_automated_install: true
omarchy_headless_install: true
```

### **Step 2: Run Installation Based on Your Choice**

#### **For Manual Installation:**
```bash
# Start the VM
make omarchy-start

# Get installation instructions
make deploy-vm-omarchy-devmachine --tags install

# Connect to console and follow prompts
# Proxmox Web UI: https://192.168.0.19:8006
# VM Console → VM 101 (omarchy-dev)
```

#### **For Semi-Automated Installation:**
```bash
# Configure for semi-automated
echo "omarchy_installation_method: semi-automated" >> android-19-proxmox/configuration-by-ansible/vm-omarchy-dev/defaults/main.yml

# Start VM and prepare configs
make omarchy-start
make deploy-vm-omarchy-devmachine --tags install,config

# Connect to console once for archinstall
# Then automation takes over
```

#### **For Custom Automation:**
```bash
# Deploy the automated Omarchy VM (completely hands-off)
make deploy-vm-omarchy-devmachine-automated

# Monitor progress
make omarchy-automated-status

# Manage the automated VM
make omarchy-automated-start
make omarchy-automated-stop
make omarchy-automated-destroy
```

---

## 📊 Quick Decision Matrix

| Factor | Manual | Semi-Automated | Custom |
|--------|--------|----------------|--------|
| **Time to Install** | 30-45 min | 15-20 min | 10-15 min* |
| **Interaction Required** | High | Medium | None** |
| **Technical Difficulty** | Low | Medium | High |
| **Troubleshooting** | Easy | Medium | Hard |
| **Repeatability** | Low | Medium | High |
| **Official Support** | ✅ Yes | ⚠️ Partial | ⚠️ Experimental |

*Cloud-init handles everything automatically
**Completely hands-off after running make command

---

## 🎯 Recommended Choice

**For most users: Start with Manual** and upgrade to Semi-Automated later if you need to deploy multiple times.

**For automation enthusiasts: Semi-Automated** gives you the best balance of automation and reliability.

**For production environments: Custom** only if you have specific requirements and expertise to handle issues.

---

## 🚦 Current Status Check

To see what installation method is currently configured:

```bash
# Check current configuration
make omarchy-status

# See available installation options
make deploy-vm-omarchy-devmachine --tags install --check
```

Ready to choose? Follow Step 1 above to configure your preferred method!