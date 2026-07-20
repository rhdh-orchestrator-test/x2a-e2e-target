# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks with InSpec testing. The migration scope is relatively small, consisting of Chef Automate deployment scripts and existing Ansible playbooks that need to be standardized. The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, Chef server configuration

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying and securing Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup, POODLE vulnerability fix

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for website deployment
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen with Ansible**: Migrate to Molecule for Ansible role testing
- **InSpec**: Consider migrating to Ansible-compatible testing frameworks like Molecule with Testinfra, or maintain InSpec as a standalone testing tool

### Security Considerations

- **SSL Configuration**: Maintain the SSL hardening in the poodle_fix.yml playbook
- **SSH Security**: Preserve the SSH security controls tested by the ssh_profile.rb InSpec test
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates in the website_https.yml playbook
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Integration**: Ensuring continued compliance testing with InSpec or migrating to an Ansible-compatible testing framework
- **Chef Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate functionality
- **SSL Certificate Management**: Ensuring proper handling of SSL certificates in the migrated Ansible roles

### Migration Order

1. **chef-and-ansible** (low risk, already Ansible): Standardize and improve the existing Ansible playbooks
2. **setup-automate** (moderate complexity): Create new Ansible roles to replace Chef Automate deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, as indicated by the README.md in the chef-and-ansible directory.
2. The setup-automate scripts are used for deploying Chef Automate and Chef Infra Server, which will need to be replaced with Ansible-based configuration management.
3. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already functional and can be standardized rather than completely rewritten.
4. The InSpec tests are valuable for compliance verification and should be preserved or migrated to an Ansible-compatible testing framework.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be flexible enough to work on other environments.
6. No complex Chef cookbooks or recipes are present in this repository, simplifying the migration process.
7. The hardcoded credentials in the setup-automate scripts are for demonstration purposes and will be replaced with Ansible Vault in the migration.