# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring proper integration between components

The estimated timeline for migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Chef setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy only Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `inspec` Ansible module

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening for Apache (POODLE vulnerability fix)
  - Migration approach: Preserve the same configuration in Ansible tasks
  
- **SSH Hardening**: InSpec profile for SSH security compliance
  - Migration approach: Create equivalent Ansible tasks to enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup steps
  
- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible deployment
  - Mitigation: Use the Ansible `inspec` module to run compliance tests

- **SSL Certificate Management**: Maintaining proper SSL certificate generation and configuration
  - Mitigation: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks

### Migration Order

1. **chef-automate-deployment** (high complexity, high value)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Replace hardcoded credentials with Ansible Vault

2. **website-https-deployment** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Ensure proper integration with InSpec tests

3. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https-deployment playbook

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. InSpec will continue to be used for compliance testing alongside Ansible
3. The Chef Automate and Chef Infra Server deployment scripts are the main components requiring migration
4. The existing Ansible playbooks will be preserved with minimal changes
5. The hardcoded credentials in the setup scripts are for demonstration purposes only
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. No external dependencies or integrations beyond what's visible in the repository