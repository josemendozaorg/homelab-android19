"""pytest-bdd configuration and step definition imports.

This file ensures all step definitions are loaded for pytest-bdd scenarios.
"""
import pytest
import subprocess
from pathlib import Path

# Import all step definition modules to register them with pytest-bdd
pytest_plugins = [
    "tests.bdd.step_defs.test_vm_llm_gpu_passthrough_steps",
    "tests.bdd.step_defs.test_rgb_led_control_steps",
    "tests.bdd.step_defs.test_ram_led_control_steps",
    "tests.bdd.step_defs.test_coolify_platform_steps",
    "tests.bdd.step_defs.test_adguard_dhcp_server_steps",
]


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory (android-19-proxmox)."""
    # tests/bdd/conftest.py -> tests/bdd -> tests -> android-19-proxmox
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def docker_compose_cmd():
    """Docker compose command prefix."""
    return "docker compose"


@pytest.fixture(scope="session")
def ansible_exec(docker_compose_cmd):
    """Ansible execution command via Docker."""
    return f"{docker_compose_cmd} exec -T homelab-dev"


@pytest.fixture(scope="session")
def inventory_file():
    """Path to Ansible inventory file."""
    return "inventory.yml"


@pytest.fixture
def ansible_runner(ansible_exec, inventory_file, project_root):
    """Helper to run Ansible commands via Docker."""
    def run(playbook, extra_vars=None, check=False, tags=None):
        """Run an Ansible playbook.

        Args:
            playbook: Path to playbook relative to project root
            extra_vars: Dict of extra variables to pass
            check: Run in check mode (no changes)
            tags: Tags to run

        Returns:
            subprocess.CompletedProcess result
        """
        cmd = [
            ansible_exec,
            "ansible-playbook",
            "--inventory", inventory_file,
            playbook,
        ]

        if check:
            cmd.append("--check")

        if tags:
            cmd.extend(["--tags", tags])

        if extra_vars:
            # Use JSON format for extra vars to properly handle types
            import json
            vars_json = json.dumps(extra_vars)
            cmd.extend(["--extra-vars", f"'{vars_json}'"])

        # Run from project root
        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )

        return result

    return run


@pytest.fixture
def ssh_runner(ansible_exec, project_root):
    """Helper to run SSH commands via Docker."""
    def run(host, command, user="root"):
        """Run SSH command.

        Args:
            host: Target host IP or hostname
            command: Command to execute
            user: SSH user (default: root)

        Returns:
            subprocess.CompletedProcess result
        """
        ssh_cmd = f"{ansible_exec} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o GlobalKnownHostsFile=/dev/null {user}@{host} '{command}'"

        result = subprocess.run(
            ssh_cmd,
            shell=True,
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )

        return result

    return run


@pytest.fixture
def terraform_runner(ansible_exec, project_root):
    """Helper to run Terraform commands via Docker."""
    def run(command, cwd=None, capture_output=True):
        """Run Terraform command.

        Args:
            command: Terraform command (e.g., 'init', 'plan', 'apply')
            cwd: Working directory (default: provisioning-by-terraform)
            capture_output: Capture stdout/stderr (default: True)

        Returns:
            subprocess.CompletedProcess result
        """
        if cwd is None:
            cwd = "android-19-proxmox/provisioning-by-terraform"

        # Build terraform command
        tf_cmd = f"{ansible_exec} terraform -chdir={cwd} {command}"

        result = subprocess.run(
            tf_cmd,
            shell=True,
            cwd=str(project_root),
            capture_output=capture_output,
            text=True,
        )

        return result

    return run


@pytest.fixture(scope="session")
def test_context():
    """Shared test context for BDD scenarios."""
    return {}
