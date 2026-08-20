# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while ensuring they follow best practices
3. Maintaining Chef InSpec tests as they are compatible with Ansible workflows

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure web server with InSpec tests
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec tests
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/org creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as-is for compliance testing with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain with Ansible provisioner

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible roles.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests verify SSH security configurations.
  - Migration approach: Maintain InSpec tests and implement corresponding Ansible tasks

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture.
  - Mitigation: Create an Ansible role that handles the installation and configuration of Chef Automate components

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible-managed systems.
  - Mitigation: Use Ansible's `community.general.inspec` module or maintain Test Kitchen with Ansible provisioner

### Migration Order

1. **setup-automate scripts** (high value, moderate complexity)
   - Convert bash scripts to Ansible roles for Chef server deployment
   - Implement Ansible Vault for credential management

2. **Existing Ansible playbooks** (low risk, high value)
   - Refactor according to Ansible best practices
   - Organize into proper roles and collections
   - Maintain InSpec tests as-is

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. InSpec tests should be preserved as they demonstrate compliance automation
3. The hardcoded credentials in the scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The deployment scripts are intended for on-premises or cloud VMs
6. The existing Ansible playbooks are functional but may not follow best practices
7. Test Kitchen is used for testing Ansible playbooks with InSpec verification