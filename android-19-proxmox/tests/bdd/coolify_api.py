"""Coolify API Client for BDD testing.

Provides a Python client for interacting with Coolify REST API
to automate application deployment testing.
"""
import requests
import time
from typing import Dict, List, Optional


class CoolifyAPIClient:
    """Client for Coolify REST API v1."""

    def __init__(self, base_url: str, email: str, password: str):
        """Initialize Coolify API client.

        Args:
            base_url: Base URL of Coolify instance (e.g., http://192.168.0.160:8000)
            email: Admin email for authentication
            password: Admin password for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (email, password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def health_check(self) -> bool:
        """Check if Coolify is accessible and healthy.

        Returns:
            True if Coolify is responding, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_sources(self) -> List[Dict]:
        """Get all configured Git sources.

        Returns:
            List of Git source configurations (GitHub, GitLab, etc.)
        """
        response = self.session.get(f"{self.base_url}/api/v1/sources")
        response.raise_for_status()
        return response.json()

    def get_github_source(self) -> Optional[Dict]:
        """Get GitHub source configuration if it exists.

        Returns:
            GitHub source dict or None if not configured
        """
        sources = self.get_sources()
        github_sources = [s for s in sources if s.get('type') == 'github']
        return github_sources[0] if github_sources else None

    def create_application(
        self,
        source_id: str,
        repository: str,
        branch: str = "main",
        build_pack: str = "dockerfile",
        environment: str = "production",
        name: Optional[str] = None
    ) -> Dict:
        """Create a new application from a GitHub repository.

        Args:
            source_id: ID of the GitHub source
            repository: Repository name (e.g., "owner/repo")
            branch: Git branch to deploy (default: main)
            build_pack: Build method (default: dockerfile)
            environment: Deployment environment (default: production)
            name: Application name (optional, defaults to repo name)

        Returns:
            Created application dict
        """
        payload = {
            'source_id': source_id,
            'repository': repository,
            'branch': branch,
            'build_pack': build_pack,
            'environment': environment,
        }
        if name:
            payload['name'] = name

        response = self.session.post(
            f"{self.base_url}/api/v1/applications",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def deploy_application(self, app_id: str) -> Dict:
        """Trigger deployment for an application.

        Args:
            app_id: Application ID or UUID

        Returns:
            Deployment result dict
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/applications/{app_id}/deploy"
        )
        response.raise_for_status()
        return response.json()

    def get_application(self, app_id: str) -> Dict:
        """Get application details and status.

        Args:
            app_id: Application ID or UUID

        Returns:
            Application details dict
        """
        response = self.session.get(
            f"{self.base_url}/api/v1/applications/{app_id}"
        )
        response.raise_for_status()
        return response.json()

    def get_deployment_status(self, app_id: str) -> str:
        """Get current deployment status for an application.

        Args:
            app_id: Application ID or UUID

        Returns:
            Status string (e.g., 'running', 'deploying', 'failed', 'stopped')
        """
        app = self.get_application(app_id)
        return app.get('status', 'unknown')

    def get_deployment_logs(self, app_id: str) -> str:
        """Get deployment logs for an application.

        Args:
            app_id: Application ID or UUID

        Returns:
            Deployment logs as string
        """
        response = self.session.get(
            f"{self.base_url}/api/v1/applications/{app_id}/logs"
        )
        response.raise_for_status()
        return response.text

    def wait_for_deployment(
        self,
        app_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> bool:
        """Wait for deployment to complete (success or failure).

        Args:
            app_id: Application ID or UUID
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between status checks in seconds (default: 5)

        Returns:
            True if deployment succeeded, False if failed or timed out

        Raises:
            TimeoutError: If deployment doesn't complete within timeout
            Exception: If deployment fails
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_deployment_status(app_id)

            if status == 'running':
                return True
            elif status in ['failed', 'error']:
                logs = self.get_deployment_logs(app_id)
                raise Exception(f"Deployment failed with status: {status}\nLogs:\n{logs}")

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Deployment timeout after {timeout}s. "
            f"Last status: {self.get_deployment_status(app_id)}"
        )

    def delete_application(self, app_id: str) -> None:
        """Delete an application.

        Args:
            app_id: Application ID or UUID
        """
        response = self.session.delete(
            f"{self.base_url}/api/v1/applications/{app_id}"
        )
        response.raise_for_status()

    def get_application_url(self, app_id: str) -> str:
        """Get the public URL for accessing an application.

        Args:
            app_id: Application ID or UUID

        Returns:
            Application URL (FQDN)
        """
        app = self.get_application(app_id)
        return app.get('fqdn', '')
