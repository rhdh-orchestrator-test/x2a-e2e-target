# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts (in the `setup-automate` directory)
2. Ansible playbooks for configuring HTTPS websites with Apache (in the `chef-and-ansible` directory)
3. InSpec tests for compliance verification (in the `chef-and-ansible/tests` directory)

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec tests continue to work with the migrated infrastructure. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring Apache HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL setup, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with alternative configuration management approach (Ansible AWX/Tower)
- **InSpec**: Can be retained as a testing framework, but will need to be integrated with Ansible workflow
- **Test Kitchen**: Replace with Ansible-native testing frameworks like Molecule

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL security improvements in the POODLE fix playbook
- **SSH Security**: The InSpec profile for SSH security must continue to be enforced
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain
  - The following credentials were detected:
    - In `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`: 
      - Username: jtonello
      - Password: password (hardcoded)
      - Email: jtonello@chef.lab

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible-only infrastructure
- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality
- **User Management**: Migrating the user and organization creation from Chef to Ansible

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Minimal changes needed to `website_https.yml` and `poodle_fix.yml`
   - Update to use Ansible best practices and remove any Chef-specific references

2. **InSpec Tests** (Moderate complexity)
   - Integrate InSpec tests with Ansible workflow
   - Replace Test Kitchen with Molecule for testing

3. **Chef Server Deployment** (High complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement user and organization management in Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, as indicated in the README.md
2. The Chef server deployment scripts are used for setting up a test environment, not production infrastructure
3. The InSpec tests are essential and must be preserved in the migration
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No actual Chef cookbooks or recipes are present in the repository that need migration
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. The Apache configuration is relatively simple and can be directly migrated to Ansible