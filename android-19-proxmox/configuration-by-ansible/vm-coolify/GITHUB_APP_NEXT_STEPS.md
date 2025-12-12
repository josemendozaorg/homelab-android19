# GitHub App Manifest Flow - Next Steps

You generated a manifest. To complete the GitHub App creation:

1. Open: https://github.com/settings/apps/new
2. Paste the manifest from: /workspace/android-19-proxmox/configuration-by-ansible/vm-coolify/github-app-manifest-generated.json
3. Click "Create GitHub App from manifest"
4. Copy the CODE from the redirect URL
5. Run the callback handler:

   ansible-playbook --inventory inventory.yml \
     android-19-proxmox/configuration-by-ansible/vm-coolify-platform.yml \
     --tags github-callback \
     -e github_app_code=YOUR_CODE_HERE

Or using the Makefile (if available):

   GITHUB_APP_CODE=YOUR_CODE_HERE make coolify-github-callback
