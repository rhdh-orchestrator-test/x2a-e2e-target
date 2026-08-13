# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The main focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on creating equivalent testing frameworks in Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - Optional CI/CD integration (Jenkins, GitLab CI, etc.)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the Ansible migration maintains:
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Secure certificate generation and storage
  - Regular certificate rotation

- **SSH Hardening**: The InSpec tests verify SSH security. Ensure the Ansible migration:
  - Disables root login
  - Implements SSH best practices
  - Provides equivalent compliance testing

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Replace with Ansible Vault for secure credential storage
  - Consider implementing HashiCorp Vault integration for enterprise deployments

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent tests in Ansible's testing framework
  - Ensuring the same level of reporting and documentation

- **Chef Automate Replacement**: Replacing Chef Automate functionality with Ansible alternatives:
  - Implementing equivalent user management
  - Setting up organization structures in AWX/Tower
  - Migrating any existing Chef data or reports

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk as they're already in Ansible format
   - May need minor updates for best practices and idempotency

2. **Testing Framework**:
   - Convert InSpec tests to Ansible testing framework
   - Implement equivalent compliance checks
   - Ensure test coverage is maintained

3. **Chef Automate/Infra Server Deployment**:
   - Create Ansible playbooks to replace the bash scripts
   - Implement secure credential management
   - Set up AWX/Tower as a replacement for Chef Automate

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The InSpec tests are used for compliance verification and not for broader infrastructure testing.

3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up demonstration environments and not for critical production infrastructure.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the migration should be flexible enough to support other environments.

6. The primary goal is to standardize on Ansible rather than maintaining a hybrid Chef/Ansible environment.