Feature: GitHub Repository Deployment (Scenario 2)
  As a developer
  I want to deploy applications from GitHub repositories via Coolify
  So that I can easily deploy and update my applications with git-based workflows

  Background:
    Given Coolify platform is running at "http://192.168.0.160:8000"
    And I have valid admin credentials

  Scenario: Deploy application from GitHub repository
    Given GitHub integration is configured in Coolify
    And I have a test repository "josemendozaorg/coolify-test-app"
    When I create a new application from the GitHub repository
    And I configure deployment settings
      | Setting        | Value                    |
      | branch         | main                     |
      | build_pack     | dockerfile               |
      | environment    | production               |
    And I trigger the deployment
    Then Coolify clones the repository from GitHub
    And Coolify builds the application using Dockerfile
    And Coolify deploys the application in a Docker container
    And application is accessible via assigned subdomain
    And application status shows "Running" in Coolify dashboard
    And deployment logs show successful build and deployment
