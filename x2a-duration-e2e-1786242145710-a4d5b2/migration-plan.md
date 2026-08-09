# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Chef InSpec test files that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible automation
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

Based on the repository analysis, this is a low-complexity migration that can be completed in approximately 1-2 weeks, as most of the configuration is already in Ansible format, and the Chef components are primarily limited to testing and server deployment.

## Module Migration Plan

This repository contains a mix of Chef and Ansible technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate `website_https_verify.rb` to Ansible Molecule tests
  - Migrate `ssh_profile.rb` to Ansible Molecule tests with STIG compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Migrate `kitchen.yml` configuration to Molecule scenario configuration

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform
  - Replace `deploy-automate.sh` and `deploy-chef-server.sh` with Ansible playbooks for AAP deployment

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache web server
  - Migration approach: Maintain the same SSL configuration in migrated Ansible roles
  - Ensure the openssl module usage is updated to current Ansible best practices

- **SSH Hardening**: InSpec tests verify SSH security configurations
  - Migration approach: Create Ansible role for SSH hardening that implements the same controls
  - Add Ansible Molecule tests to verify SSH security compliance

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` scripts
    - Migration approach: Replace with Ansible Vault for secure credential storage
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation: Use Ansible Molecule with testinfra or use the ansible-lint tool with custom rules
  - Consider using ansible-test for compliance verification

- **Chef Automate Functionality**: Replacing Chef Automate functionality with Ansible Automation Platform
  - Mitigation: Map Chef Automate features to AAP equivalents
  - Develop custom dashboards in AAP for compliance reporting if needed

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and refactor `website_https.yml` and `poodle_fix.yml` to follow current Ansible best practices
   - Convert to proper Ansible roles with variables, handlers, and templates

2. **Testing Framework** (Moderate complexity)
   - Migrate InSpec tests to Ansible Molecule tests
   - Create test scenarios that verify the same compliance controls

3. **Chef Server Deployment** (High complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, as indicated by the README.md
2. The InSpec tests are used for compliance verification of configurations managed by Ansible
3. There are no actual Chef cookbooks or recipes in use, only InSpec tests and Chef server deployment scripts
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or complex infrastructure is involved
6. The repository is not used in production environments but for demonstration purposes