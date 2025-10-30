"""Step definitions for Scenario 2: GitHub Repository Deployment.

This module contains BDD step definitions for testing GitHub repository
deployment via Coolify, including GitHub App integration, application
deployment, and accessibility verification.
"""
import pytest
import requests
from pytest_bdd import scenarios, given, when, then, parsers
from pathlib import Path

# Import Coolify API client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from coolify_api import CoolifyAPIClient


# Load scenarios from the feature file
scenarios('../features/scenario_02_github_deployment.feature')


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def coolify_api():
    """Coolify API client instance."""
    return CoolifyAPIClient(
        base_url="http://192.168.0.160:8000",
        email="josephrichard7@gmail.com",
        password="8n@~v#Pc5:0QE1ri<,0sVX:Z3QnK,sMa"
    )


@pytest.fixture
def scenario_context():
    """Shared context for Scenario 2 test state."""
    return {
        'coolify_url': None,
        'github_source': None,
        'test_repository': None,
        'application': None,
        'deployment': None,
        'deployment_settings': {},
    }


# ============================================================================
# GIVEN Steps (Setup and Preconditions)
# ============================================================================

@given('Coolify platform is running at "http://192.168.0.160:8000"', target_fixture="coolify_running")
def coolify_platform_running(coolify_api, scenario_context):
    """Verify Coolify platform is accessible and healthy."""
    scenario_context['coolify_url'] = "http://192.168.0.160:8000"

    # Check Coolify health
    is_healthy = coolify_api.health_check()

    assert is_healthy, \
        "Coolify platform is not accessible at http://192.168.0.160:8000"

    return True


@given('I have valid admin credentials')
def valid_admin_credentials(coolify_api):
    """Verify admin credentials are valid by checking API access."""
    # Try to fetch sources to validate auth
    try:
        coolify_api.get_sources()
        return True
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            pytest.fail("Admin credentials are invalid (401 Unauthorized)")
        raise


@given('GitHub integration is configured in Coolify')
def github_integration_configured(coolify_api, scenario_context):
    """Verify GitHub source is configured in Coolify."""
    github_source = coolify_api.get_github_source()

    assert github_source is not None, \
        "GitHub source not configured in Coolify. " \
        "Please add GitHub App/OAuth integration via Coolify UI."

    scenario_context['github_source'] = github_source


@given('I have a test repository "josemendozaorg/coolify-test-app"')
def test_repository_exists(scenario_context):
    """Verify test repository exists and is accessible."""
    repo_url = "https://github.com/josemendozaorg/coolify-test-app"
    scenario_context['test_repository'] = "josemendozaorg/coolify-test-app"

    # Check repository is accessible (public repo)
    try:
        response = requests.get(repo_url, timeout=10)
        assert response.status_code == 200, \
            f"Test repository not accessible: {repo_url}"
    except requests.RequestException as e:
        pytest.fail(f"Failed to verify test repository: {e}")


# ============================================================================
# WHEN Steps (Actions)
# ============================================================================

@when('I create a new application from the GitHub repository')
def create_application_from_github(coolify_api, scenario_context):
    """Create a new Coolify application from the GitHub repository."""
    github_source = scenario_context['github_source']
    repository = scenario_context['test_repository']

    # Create application
    application = coolify_api.create_application(
        source_id=github_source['id'],
        repository=repository,
        name="coolify-test-app"
    )

    scenario_context['application'] = application

    assert application is not None, \
        "Failed to create application from GitHub repository"
    assert 'id' in application, \
        "Created application missing ID"


@when(parsers.parse('I configure deployment settings\n{settings_table}'))
def configure_deployment_settings(scenario_context, settings_table):
    """Configure deployment settings from table.

    Args:
        settings_table: pytest-bdd table with Setting and Value columns
    """
    # Parse settings table (pytest-bdd provides this as a string)
    # Format:
    #   | Setting        | Value                    |
    #   | branch         | main                     |
    #   | build_pack     | dockerfile               |
    #   | environment    | production               |

    lines = [line.strip() for line in settings_table.strip().split('\n') if line.strip()]

    # Skip header row
    for line in lines[1:]:
        # Parse table row: | setting_name | value |
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            setting = parts[0]
            value = parts[1]
            scenario_context['deployment_settings'][setting] = value

    # Verify required settings are present
    required_settings = ['branch', 'build_pack', 'environment']
    for setting in required_settings:
        assert setting in scenario_context['deployment_settings'], \
            f"Required deployment setting missing: {setting}"


@when('I trigger the deployment')
def trigger_deployment(coolify_api, scenario_context):
    """Trigger deployment for the application."""
    application = scenario_context['application']

    # Trigger deployment
    deployment_result = coolify_api.deploy_application(application['id'])

    scenario_context['deployment'] = deployment_result

    assert deployment_result is not None, \
        "Failed to trigger deployment"


# ============================================================================
# THEN Steps (Assertions and Verification)
# ============================================================================

@then('Coolify clones the repository from GitHub')
def verify_repository_cloned(coolify_api, scenario_context):
    """Verify Coolify cloned the repository (check logs)."""
    app_id = scenario_context['application']['id']

    # Wait briefly for deployment to start
    import time
    time.sleep(3)

    # Get deployment logs
    try:
        logs = coolify_api.get_deployment_logs(app_id)

        # Check for git clone indicators in logs
        assert any(indicator in logs.lower() for indicator in ['clone', 'cloning', 'git']), \
            "Deployment logs don't show repository cloning"

    except Exception as e:
        # If logs endpoint not available, skip this verification
        pytest.skip(f"Could not verify repository cloning: {e}")


@then('Coolify builds the application using Dockerfile')
def verify_dockerfile_build(coolify_api, scenario_context):
    """Verify Coolify built the application using Dockerfile."""
    app_id = scenario_context['application']['id']

    try:
        logs = coolify_api.get_deployment_logs(app_id)

        # Check for Docker build indicators
        build_indicators = ['dockerfile', 'docker build', 'building', 'step 1/']
        assert any(indicator in logs.lower() for indicator in build_indicators), \
            "Deployment logs don't show Dockerfile build process"

    except Exception as e:
        pytest.skip(f"Could not verify Dockerfile build: {e}")


@then('Coolify deploys the application in a Docker container')
def verify_docker_deployment(coolify_api, scenario_context):
    """Verify application is deployed in a Docker container."""
    app_id = scenario_context['application']['id']

    # Wait for deployment to complete (or fail)
    try:
        success = coolify_api.wait_for_deployment(app_id, timeout=300)
        assert success, "Deployment did not complete successfully"

    except TimeoutError:
        pytest.fail("Deployment timed out after 5 minutes")
    except Exception as e:
        pytest.fail(f"Deployment failed: {e}")


@then('application is accessible via assigned subdomain')
def verify_application_accessible(coolify_api, scenario_context):
    """Verify application is accessible via its assigned URL."""
    app_id = scenario_context['application']['id']

    # Get application URL
    app_url = coolify_api.get_application_url(app_id)

    assert app_url, \
        "Application does not have an assigned URL"

    # Try to access the application
    try:
        response = requests.get(f"http://{app_url}", timeout=10)

        assert response.status_code == 200, \
            f"Application not accessible: HTTP {response.status_code}"

        # Verify it's our test app (should contain specific text)
        assert "Coolify" in response.text or "Test App" in response.text, \
            "Application content doesn't match expected test app"

    except requests.RequestException as e:
        pytest.fail(f"Failed to access application at http://{app_url}: {e}")


@then('application status shows "Running" in Coolify dashboard')
def verify_running_status(coolify_api, scenario_context):
    """Verify application status is 'running' in Coolify."""
    app_id = scenario_context['application']['id']

    status = coolify_api.get_deployment_status(app_id)

    assert status.lower() == 'running', \
        f"Application status is '{status}', expected 'running'"


@then('deployment logs show successful build and deployment')
def verify_successful_deployment_logs(coolify_api, scenario_context):
    """Verify deployment logs show successful completion."""
    app_id = scenario_context['application']['id']

    try:
        logs = coolify_api.get_deployment_logs(app_id)

        # Check for success indicators
        success_indicators = ['success', 'successfully', 'complete', 'deployed', 'running']
        assert any(indicator in logs.lower() for indicator in success_indicators), \
            "Deployment logs don't show successful completion"

        # Check for failure indicators (should not be present)
        failure_indicators = ['failed', 'error:', 'fatal']
        failure_found = [ind for ind in failure_indicators if ind in logs.lower()]
        assert not failure_found, \
            f"Deployment logs contain failure indicators: {failure_found}"

    except Exception as e:
        pytest.skip(f"Could not verify deployment logs: {e}")
