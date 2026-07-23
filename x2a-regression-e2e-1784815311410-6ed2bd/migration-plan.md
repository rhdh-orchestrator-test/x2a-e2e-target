# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing framework like Molecule
- **InSpec**: Maintain as a compliance testing tool, which works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain secure SSL settings.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests verify SSH security configurations.
  - Migration approach: Implement Ansible tasks to enforce SSH security settings tested by InSpec

- **Vault/secrets management**:
  - Hardcoded credentials in bash scripts (username, password, email)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture.
  - Mitigation: Create an Ansible role that handles Chef Automate installation and configuration, or replace Chef Automate with Ansible AWX/Tower

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible.
  - Mitigation: Use Ansible's built-in integration with InSpec or convert tests to Ansible assert statements where appropriate

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format, just need review and potential enhancement
2. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity, requires creating equivalent Ansible roles

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. InSpec will continue to be used for compliance testing alongside Ansible
3. The hardcoded credentials in the bash scripts are for demonstration purposes only
4. The target environment will continue to be Ubuntu 20.04 or similar Debian-based distributions
5. The Apache web server configuration requirements will remain the same
6. The Chef Automate/Infra Server deployment is a one-time setup rather than ongoing configuration management