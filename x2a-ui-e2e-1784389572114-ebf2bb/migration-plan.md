# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Security hardening, service restart handlers

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port checking, HTTP response validation, SSL protocol verification, SSH configuration validation

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page. No migration needed, can be used as-is.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Should be converted to an Ansible role.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Should be converted to an Ansible role or included in the HTTPS role.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to Ansible playbooks.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to Ansible playbooks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning can be handled by OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible roles

- **SSH Hardening**: The SSH security profile needs to be converted to Ansible-compatible tests
  - Approach: Create equivalent checks using Ansible assert or Molecule verify phase

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Create custom Ansible modules or use assert statements to perform equivalent checks
  - Consider using Molecule's verify phase with testinfra for similar functionality

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible management
  - Mitigation: Document the transition from Chef Server to Ansible AWX/Tower or other management tools
  - Create Ansible playbooks to set up the chosen management infrastructure

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need organization into proper roles
2. **InSpec Tests** (tests directory): Moderate complexity to convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (setup-automate directory): High complexity, requires architectural decisions about replacement infrastructure

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use, based on the README.md content.
2. The InSpec tests are meant to validate the configurations applied by the Ansible playbooks.
3. The deployment scripts are intended for setting up a test environment rather than production.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.
5. The repository assumes Ubuntu 20.04 as the target platform, which may need to be expanded if other platforms need to be supported.
6. The current implementation uses self-signed certificates, which may need to be replaced with proper certificate management in production.