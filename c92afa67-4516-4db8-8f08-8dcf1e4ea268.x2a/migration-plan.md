# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance verification

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache, SSL certificates, and proper configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platform
  - Migration strategy: Create Ansible playbooks to install and configure AWX/Tower
  - Consider containerized deployment using Docker/Kubernetes

- **Test Kitchen with Ansible**: Replace with Molecule for Ansible role/playbook testing
  - Migration strategy: Create Molecule scenarios equivalent to existing Test Kitchen configurations

- **InSpec Tests**: Maintain as-is or convert to Ansible-native testing frameworks
  - Migration strategy: Keep InSpec tests for compliance verification, integrate with Ansible using the `inspec` Ansible module

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates
  - Migration approach: Maintain the same approach but consider using Ansible Vault for storing sensitive information

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Chef Server User Management**: The Chef scripts create users and organizations
  - Mitigation: Create equivalent Ansible playbooks for AWX/Tower user management

- **InSpec Integration**: Maintaining InSpec tests with Ansible
  - Mitigation: Use the Ansible `inspec` module to run InSpec tests as part of playbooks

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml) - Low risk, already in Ansible format
   - Review and enhance existing playbooks
   - Add Ansible Vault for sensitive data

2. **Chef Automate/Infra Server Scripts** (setup-automate/*.sh) - Medium complexity
   - Convert to Ansible playbooks for AWX/Tower deployment
   - Implement user and organization management in Ansible

3. **Testing Framework** (kitchen.yml) - Medium complexity
   - Migrate from Test Kitchen to Molecule
   - Ensure InSpec tests continue to work with new testing framework

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. The Chef InSpec tests are intended to be maintained as a compliance verification tool
3. The target environment will continue to be Ubuntu 20.04 or similar
4. The deployment scripts are intended for single-node installations
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The migration will maintain the same functionality but using Ansible-native approaches
7. User management will be handled by AWX/Tower or another Ansible management platform