# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating the Ansible configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The main focus will be on replacing the Chef InSpec tests with Ansible-native testing solutions and converting the Chef Automate/Infra Server deployment scripts to Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the Ansible `uri` module to replace HTTP/HTTPS validation tests

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enforced
  - Maintain proper certificate generation and management

- **Credentials Management**: 
  - Current scripts contain hardcoded credentials (username, password)
  - Migration should use Ansible Vault for secure credential storage
  - Implement proper secret rotation mechanisms

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Count: 2 credential sets identified

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a test mapping document and validate each test case individually

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Document the specific Chef Server features in use and identify Ansible alternatives

- **Maintaining Test Coverage**: Ensuring the same level of compliance testing during migration
  - Mitigation: Implement parallel testing with both old and new systems during transition

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Convert any Chef-specific idioms to Ansible best practices

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Ensure security hardening is maintained

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   - Validate test coverage matches original InSpec tests

4. **Chef Automate/Server deployment scripts** (high complexity)
   - Convert shell scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The current setup uses Test Kitchen primarily for testing Ansible playbooks, not for Chef cookbook development
2. The InSpec tests are used for compliance validation of infrastructure deployed by Ansible
3. The Chef Automate and Chef Infra Server deployments are separate from the main application infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. There is no complex Chef cookbook development happening in this repository
6. The migration will maintain the same level of security compliance testing
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only