# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while ensuring they follow best practices
3. Maintaining Chef InSpec tests as a compliance verification layer

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the repository primarily contains deployment scripts and simple Ansible playbooks rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec testing
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Consider migrating to Molecule for Ansible role testing
- **InSpec**: Maintain as compliance testing framework, integrate with Ansible workflow

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols (SSL3)
  - Migration approach: Maintain this security configuration in Ansible roles
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible role to enforce SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates generated during deployment
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires understanding of Chef Automate architecture
  - Mitigation: Create an Ansible role that handles the same configuration steps as the bash script

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation: Use Ansible's built-in integration with InSpec or create a custom module

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, already in Ansible)
   - Review and refactor existing Ansible playbooks to follow best practices
   - Organize into proper roles and collections structure

2. **setup-automate Bash Scripts** (medium complexity)
   - Convert bash scripts to Ansible roles for deploying infrastructure
   - Replace hardcoded credentials with Ansible Vault

3. **Testing Framework** (medium complexity)
   - Migrate from Test Kitchen to Molecule for Ansible testing
   - Maintain InSpec tests for compliance verification

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README.md description.
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which will be replaced by Ansible.
3. The InSpec tests are valuable for compliance verification and should be maintained.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management.
5. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
6. The Apache configuration in the Ansible playbooks is a simple example and not a complex production configuration.
7. There are no external dependencies or integrations beyond what is visible in the repository.