# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks with minor improvements
3. Maintaining Chef InSpec tests as they are already compatible with Ansible

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope and existing Ansible content.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec testing
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration against POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate with Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing approach
- **InSpec**: Maintain as is, as InSpec works well with Ansible for compliance testing

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and hardening against POODLE vulnerability
  - Migration approach: Maintain existing Ansible tasks but update to use more modern Ansible modules
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Maintain InSpec tests, add corresponding Ansible tasks to enforce SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts
  - Consider using the `command` module for Chef-specific commands that don't have Ansible equivalents

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible
  - Mitigation: Use Ansible's built-in support for InSpec or create a custom Ansible module

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Update `website_https.yml` and `poodle_fix.yml` to use more modern Ansible practices
   - Maintain InSpec tests as they are

2. **Chef Deployment Scripts** (Moderate complexity)
   - Convert `deploy-chef-server.sh` to an Ansible playbook
   - Convert `deploy-automate.sh` to an Ansible playbook
   - Implement Ansible Vault for credential storage

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. InSpec tests should be maintained as they demonstrate compliance automation with Ansible
3. The Chef deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or complex infrastructure beyond what's visible in the repository
6. No CI/CD pipeline integration is required for the migration
7. The hardcoded credentials in the scripts are for demonstration purposes only