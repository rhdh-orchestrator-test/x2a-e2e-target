# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks used for demonstration purposes. The repository appears to be focused on showing how Chef InSpec can be used alongside Ansible for compliance automation, rather than being a production infrastructure codebase. The migration scope is relatively small, with only a few Ansible playbooks and Chef setup scripts to consider. The estimated timeline for migration would be 1-2 days given the limited scope.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks in a Vagrant environment
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Consider maintaining InSpec as a separate testing tool that works alongside Ansible

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Use existing Vagrant configuration if needed for development environments

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Use the `openssl_*` modules already present in the Ansible playbooks

- **SSH Hardening**: The InSpec tests check for SSH root login configuration.
  - Migration approach: Ensure SSH hardening is included in the migrated Ansible roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef setup scripts contain hardcoded usernames and passwords
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate/Infra Server Setup**: The bash scripts for setting up Chef infrastructure will need to be replaced with Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef server deployment if still needed, or completely replace with Ansible-based infrastructure management

- **InSpec Testing Integration**: The repository demonstrates using InSpec with Ansible for compliance testing.
  - Mitigation strategy: Either maintain InSpec as a separate tool or migrate tests to Ansible-native testing approaches

### Migration Order

1. `website_https.yml` and `poodle_fix.yml` (already Ansible playbooks, just need review and potential refactoring)
2. Test Kitchen configuration (replace with Molecule)
3. Chef server deployment scripts (create Ansible equivalents if needed)

### Assumptions

1. The repository is primarily for demonstration purposes and not a production infrastructure codebase
2. The InSpec tests are meant to show compliance automation alongside Ansible, not necessarily as part of a Chef-managed infrastructure
3. The Chef Automate/Infra Server setup scripts may not need migration if the goal is to move entirely to Ansible
4. The hardcoded credentials in the setup scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 running on Vagrant VMs