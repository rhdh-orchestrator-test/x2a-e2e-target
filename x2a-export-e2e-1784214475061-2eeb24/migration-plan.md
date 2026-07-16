# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on infrastructure automation and compliance testing. The primary migration scope involves:

1. Chef Automate and Chef Infra Server deployment scripts
2. Chef InSpec compliance tests that are currently used alongside Ansible playbooks

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The main focus will be on converting the Chef server deployment scripts to Ansible and ensuring the InSpec tests continue to work with the migrated infrastructure. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts with Chef server installation
    - Key Features: User creation, organization setup, server configuration

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone testing tool (recommended if tests are complex)

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

### Security Considerations

- **SSH Configuration**: The InSpec profile tests for SSH root login restrictions, which should be maintained in the Ansible migration
- **SSL/TLS Configuration**: The playbooks configure TLS 1.2 and disable older protocols, which should be preserved
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef server deployment scripts (username, password)
  - SSL certificates generated and managed in the playbooks
  - Recommendation: Use Ansible Vault to secure the credentials currently hardcoded in the bash scripts

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef server installation
  - Handling the user and organization creation with Ansible modules
  - Managing the PEM key files securely

- **InSpec Test Integration**: Ensuring the InSpec tests continue to work with the Ansible-managed infrastructure:
  - Option 1: Convert InSpec tests to Ansible assertions
  - Option 2: Keep InSpec and call it from Ansible using the `command` module
  - Option 3: Use Molecule with InSpec verifier

### Migration Order

1. **chef-automate-deployment** (high value, moderate complexity)
   - Convert bash scripts to Ansible roles
   - Implement secure credential management with Ansible Vault

2. **compliance-testing** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Ensure tests work with the new Ansible-managed infrastructure

3. **website-https-configuration** and **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks
   - Consolidate into roles if appropriate

### Assumptions

1. The current setup uses Test Kitchen primarily for testing Ansible playbooks with InSpec verification
2. The Chef components are limited to InSpec testing and server deployment scripts
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The security requirements include proper SSL/TLS configuration and SSH hardening
5. No complex Chef cookbooks or recipes are present that would require significant conversion effort
6. The deployment scripts are designed for both on-premises and cloud environments
7. The hardcoded credentials in the deployment scripts are for testing purposes only