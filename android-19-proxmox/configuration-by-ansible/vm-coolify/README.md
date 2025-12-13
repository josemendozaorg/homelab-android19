# Coolify Platform Configuration

Ansible role for configuring Coolify Platform (Self-hosted PaaS) with automated wildcard domain setup.

## Features

- ✅ Docker installation
- ✅ Coolify platform installation
- ✅ **Automated wildcard domain configuration via API**
- ✅ **Automated GitHub App source registration via API**
- ✅ API token validation via .env file
- ✅ Cloud-init verification

## Prerequisites

### 1. VM Deployment
VM must be deployed via Terraform first:
```bash
make deploy-vm-coolify-containerplatform
```

### 2. API Token Creation (One-time Setup)

Create an API token manually via Coolify UI:

1. Access Coolify: http://192.168.0.160:8000
2. Log in with admin credentials (shown during first deployment)
3. Navigate to: **Settings → Security → API Tokens**
4. Click **"Create New Token"**
   - **Name**: `ansible-automation`
   - **Permissions**: Uncheck "Read Only" to get full `*` permissions
5. **Copy the token** (shown only once!)
6. Save token using one of the methods below:

#### Option A: .env File (Recommended)
```bash
cd android-19-proxmox/configuration-by-ansible/vm-coolify
cp .env.example .env
# Edit .env and add your token:
# COOLIFY_API_TOKEN=your_actual_token_here
```

#### Option B: Environment Variable
```bash
export COOLIFY_API_TOKEN="your_actual_token_here"
```

### 3. GitHub App Setup (Optional - for Repository Deployments)

To enable automated deployments from GitHub repositories, you can create a GitHub App using one of two methods:

#### Option A: Manifest Flow (Semi-Automated - Recommended)

This method reduces GitHub App creation from ~15 manual clicks to 1 click + paste.

**Step 1: Generate Manifest**
```bash
# Run full deployment with manifest generation
make deploy-vm-coolify-containerplatform

# Or generate manifest only:
docker compose exec -T homelab-dev \
  ansible-playbook --inventory inventory.yml \
  android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
  --tags github-manifest
```

**Step 2: Create App via Manifest**
The playbook will output a manifest JSON and instructions. Follow them:
1. Copy the manifest JSON from the output
2. Open: https://github.com/settings/apps/new
3. Paste the manifest and click "Create GitHub App from manifest"
4. Copy the `code` parameter from the redirect URL

**Step 3: Process Callback**
```bash
# Exchange code for credentials
docker compose exec -T homelab-dev \
  ansible-playbook --inventory inventory.yml \
  android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
  --tags github-callback \
  -e github_app_code=YOUR_CODE_HERE
```

**Step 4: Install App**
Install the GitHub App to your repositories:
1. Go to: https://github.com/apps/your-app-name
2. Click "Install" or "Configure"
3. Select repositories to grant access
4. If installation_id wasn't auto-detected, manually add it to `.env`:
   ```bash
   GITHUB_INSTALLATION_ID=12345678
   ```

**Step 5: Register with Coolify**
```bash
# Full deployment (includes GitHub source registration)
make deploy-vm-coolify-containerplatform

# Or just register GitHub source:
docker compose exec -T homelab-dev \
  ansible-playbook --inventory inventory.yml \
  android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
  --tags github-source
```

#### Option B: Manual Creation (Full Control)

Create a GitHub App manually with full control over all settings:

1. **Create GitHub App**: https://github.com/settings/apps/new
   - **GitHub App name**: `coolify-homelab`
   - **Homepage URL**: `http://192.168.0.160:8000`
   - **Webhook URL**: `http://192.168.0.160:8000/webhooks/github`
   - **Webhook secret**: Generate random string (save for .env)
   - **Permissions** (Repository):
     - Contents: Read & write
     - Metadata: Read-only
     - Pull requests: Read & write
     - Webhooks: Read & write
   - **Subscribe to events**: Push, Pull request

2. **Generate Private Key**
   - After creating the app, click "Generate a private key"
   - Download the `.pem` file
   - Copy the entire contents (including `-----BEGIN` and `-----END` lines)

3. **Install App to Repositories**
   - Click "Install App" → Select your organization
   - Choose "All repositories" or select specific ones
   - Complete installation

4. **Copy Credentials to .env**
   ```bash
   cd android-19-proxmox/configuration-by-ansible/vm-coolify
   cp .env.example .env  # If not already done
   # Edit .env with your credentials:

   GITHUB_APP_ID=123456
   GITHUB_INSTALLATION_ID=789012
   GITHUB_CLIENT_ID=Iv1.abc123def456
   GITHUB_CLIENT_SECRET=your_client_secret_here
   GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
   GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\nMII...your_key...==\n-----END RSA PRIVATE KEY-----
   ```

5. **Register with Coolify**
   ```bash
   # Full deployment
   make deploy-vm-coolify-containerplatform

   # Or just register GitHub source:
   docker compose exec -T homelab-dev \
     ansible-playbook --inventory inventory.yml \
     android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
     --tags github-source
   ```

**Note**: GitHub App credentials are optional. If not provided, wildcard domain will still be configured, but repository deployments won't be automated.

## Usage

### Full Deployment (Without Wildcard Configuration)
```bash
make deploy-vm-coolify-containerplatform
```

### Configure Wildcard Domain (Requires API Token)

**Using .env file (recommended):**
```bash
# 1. Set up .env file once (see Prerequisites)
cd android-19-proxmox/configuration-by-ansible/vm-coolify
cp .env.example .env
# Edit .env with your token

# 2. Run full deployment
make deploy-vm-coolify-containerplatform

# Or run just wildcard configuration:
docker compose exec -T homelab-dev \
  ansible-playbook --inventory inventory.yml \
  android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
  --tags wildcard-domain
```

**Using environment variable:**
```bash
COOLIFY_API_TOKEN="your-token-here" make deploy-vm-coolify-containerplatform

# Or just wildcard configuration:
COOLIFY_API_TOKEN="your-token-here" docker compose exec -T homelab-dev \
  ansible-playbook --inventory inventory.yml \
  android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
  --tags wildcard-domain
```

## What Gets Automated

### API Token Validation (`tasks/generate-api-token.yml`)
- Reads `COOLIFY_API_TOKEN` from:
  1. `.env` file in role directory (priority)
  2. Environment variable (fallback)
- Validates token via Coolify API
- Provides clear instructions if token is missing/invalid

### Wildcard Domain Configuration (`tasks/configure-wildcard-domain.yml`)
- Fetches Coolify server UUID via API
- Attempts to configure wildcard domain: `coolify.homelab`
- **Note**: Current Coolify API (v4) may not allow wildcard domain updates via PATCH
- **Workaround**: Configure manually via UI (see Manual Configuration section below)

### GitHub Source Configuration (`tasks/configure-github-source.yml`)
- Reads GitHub App credentials from `.env` file (if provided)
- Checks if GitHub source already exists in Coolify
- Registers GitHub App with Coolify via API
- **Optional**: Skips gracefully if GitHub credentials not configured
- **Fully automated** once GitHub App is created and credentials added to .env

## Configuration Variables

Located in `defaults/main.yml`:

```yaml
# Coolify service configuration
coolify_web_port: 8000  # Coolify web UI port
coolify_wildcard_domain: "josemendoza.dev"  # Wildcard domain for deployed applications

# Admin account (created during installation)
coolify_admin_email: "josephrichard7@gmail.com"
coolify_admin_password: "{{ lookup('password', '/tmp/coolify_admin_password') }}"
```

## Wildcard Domain Configuration

### Automated (API) - Currently Limited

The playbook includes automated wildcard domain configuration via API, but current Coolify v4 may restrict this field from being updated via PATCH requests. If you see a "field not allowed" error, use the manual UI method below.

### Manual (UI) - Recommended

1. Access Coolify UI: http://192.168.0.160:8000
2. Navigate to: **Servers** → **Select your server** → **Settings**
3. Scroll to **Wildcard Domain** field
4. Enter: `http://josemendoza.dev`
5. Click **Save**

### Notes on Automation
- The `coolify_wildcard_domain` variable in `defaults/main.yml` is used for documentation and attempted API calls.
- Due to Coolify v4 API limitations, this setting often requires the manual UI step above.

### Expected Behavior

Once configured, applications deployed via Coolify will be accessible at:

```
<app-name>.<random-hash>.<environment>.coolify.homelab
```

**Example:**
```
coolify-test-app.abc123.prod.coolify.homelab
```

## DNS Requirements

AdGuard Home DNS must have wildcard entry (already configured):
```yaml
# In lxc-adguard/defaults/main.yml
- domain: "*.coolify.homelab"
  ip: "192.168.0.160"
```

This enables automatic DNS resolution for all Coolify application subdomains.

## Troubleshooting

### Token Validation Fails
```
❌ Provided COOLIFY_API_TOKEN is invalid or expired
```

**Solution**: Create a new token via Coolify UI (see Prerequisites above)

### Wildcard Domain Not Set
Check Coolify server configuration:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.0.160:8000/api/v1/servers
```

Look for `wildcard_domain` field in response.

### Cannot Access Coolify UI
1. Check VM is running: `ssh ubuntu@192.168.0.160 'docker ps | grep coolify'`
2. Check port mapping: Container should expose port 8000
3. Check DNS resolution: `dig coolify.homelab`

## Architecture

```
┌─────────────────────────────────────────────┐
│ AdGuard DNS (192.168.0.25)                 │
│ *.coolify.homelab → 192.168.0.160          │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│ Coolify Platform (192.168.0.160:8000)      │
│ ┌─────────────────────────────────────────┐ │
│ │ Traefik Reverse Proxy                  │ │
│ │ - Routes HTTP requests by Host header   │ │
│ │ - app1.hash1.prod.coolify.homelab      │ │
│ │ - app2.hash2.dev.coolify.homelab       │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ Application Containers                  │ │
│ │ - Deployed from GitHub repositories     │ │
│ │ - Automatic SSL with Let's Encrypt      │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Next Steps

After wildcard domain configuration:
1. Configure GitHub App integration (Phase 5)
2. Deploy test applications
3. Run BDD acceptance tests

## Related Documentation

- Root `CLAUDE.md` - Repository-wide guidance
- `specs/coolify-platform/coolify-platform-spec.md` - Feature specification
- `tests/bdd/features/scenario_02_github_deployment.feature` - BDD tests
