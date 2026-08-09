# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the repository already uses Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts that need individual migration planning:

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

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Continue using InSpec but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific Test Kitchen provisioner (already in use)

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use)

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms.
  - Mitigation: Use Ansible's assert module for basic tests, or consider Molecule for more complex testing scenarios.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible.
  - Mitigation: Create Ansible roles for Chef server deployment or consider migrating to Ansible Automation Platform entirely.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need review and potential refactoring.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, need conversion to Ansible testing framework.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, need complete rewrite as Ansible playbooks.

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production, based on the README content.
2. The Chef InSpec tests are used alongside Ansible for compliance verification, not as part of a larger Chef-based infrastructure.
3. The deployment scripts are examples and may contain simplified configurations not suitable for production environments (e.g., hardcoded passwords).
4. The target environment is Ubuntu 20.04 based on the Test Kitchen configuration.
5. The migration will maintain the same functionality but convert all components to Ansible-native solutions.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.