# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation, along with Chef Automate/Infra Server deployment scripts. The migration scope is focused on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Preserving existing Ansible playbooks
3. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low to medium complexity due to the small codebase and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec tests
  - Purpose: Defines the test environment using Vagrant and Ubuntu 20.04
  - Migration: Convert to Ansible Molecule configuration or maintain as-is with Ansible provisioner

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website
  - Purpose: Installs and configures Apache with SSL/TLS
  - Migration: Keep as-is, already in Ansible format

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache
  - Purpose: Updates SSL configuration to mitigate POODLE vulnerability
  - Migration: Keep as-is, already in Ansible format

- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
  - Purpose: Tests HTTPS port, content, and SSL/TLS protocols
  - Migration: Convert to Ansible assert tasks or Molecule verify tests

- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
  - Purpose: Verifies SSH root login is disabled
  - Migration: Convert to Ansible assert tasks or Molecule verify tests

- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
  - Purpose: Automates the installation of Chef Automate and Chef Infra Server
  - Migration: Convert to Ansible playbook with variables for configuration

- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only
  - Purpose: Automates the installation of Chef Infra Server
  - Migration: Convert to Ansible playbook with variables for configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Integrate with pytest-ansible for Python-based testing
  - Option 3: Use ansible-test for Ansible Collections testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the SSL/TLS security configurations in the Apache web server
  - Migration approach: Convert the existing Ansible tasks for SSL configuration without changes
  
- **SSH Security Hardening**: The InSpec tests for SSH security must be converted to equivalent Ansible checks
  - Migration approach: Use ansible-lint or custom Ansible tasks to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy scripts contain hardcoded username/password that should be migrated to Ansible Vault
  - SSL certificates: Self-signed certificates are generated in the playbooks, which should be preserved in the migration
  - Count of credentials detected: 2 (user password in setup scripts, SSL certificates in website_https.yml)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Ansible assert modules or integrate with Molecule for testing
  
- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced
  - Mitigation: Map Chef Automate features to Ansible Automation Platform or alternative tools

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - chef-and-ansible/website_https.yml
   - chef-and-ansible/poodle_fix.yml

2. **InSpec Tests** (Medium complexity)
   - chef-and-ansible/tests/website_https_verify.rb → Convert to Ansible tests
   - chef-and-ansible/tests/ssh_profile.rb → Convert to Ansible tests

3. **Chef Deployment Scripts** (High complexity)
   - setup-automate/deploy-automate.sh → Convert to Ansible playbook
   - setup-automate/deploy-chef-server.sh → Convert to Ansible playbook

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The Test Kitchen configuration is used for development and testing only
3. The Chef Automate and Chef Infra Server deployment scripts are examples and not used in production
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The self-signed SSL certificates are acceptable for the demonstration environment
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There are no external dependencies or integrations beyond what is visible in the repository
8. The migration will preserve all existing functionality while converting to pure Ansible