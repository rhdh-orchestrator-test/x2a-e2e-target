# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains Chef InSpec tests and Ansible playbooks demonstrating compliance automation, along with Chef deployment scripts. The migration scope is focused on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving existing Ansible playbooks. The estimated timeline is 1-2 weeks given the limited scope.

## Module Migration Plan

This repository contains components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions (Ansible Lint, Molecule, ansible-test)
- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX and Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: Preserve SSL/TLS hardening (disable SSLv3, enforce TLSv1.2)
- **SSH Hardening**: Migrate SSH profile tests to equivalent Ansible tests
- **Vault/secrets management**: Migrate hardcoded credentials to Ansible Vault (3 credentials detected)

### Technical Challenges

- **Test Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks
- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem

### Migration Order

1. **Ansible Playbooks** (Low risk)
   - chef-and-ansible/website_https.yml
   - chef-and-ansible/poodle_fix.yml

2. **InSpec Tests** (Moderate complexity)
   - chef-and-ansible/tests/website_https_verify.rb
   - chef-and-ansible/tests/ssh_profile.rb

3. **Chef Deployment Scripts** (High complexity)
   - setup-automate/deploy-automate.sh
   - setup-automate/deploy-chef-server.sh

### Assumptions

1. Repository is for demonstration purposes rather than production deployment
2. Test Kitchen configuration is for development and testing only
3. Deployment scripts are examples and not used in production
4. Hardcoded credentials are for demonstration purposes only
5. Target environment is Ubuntu 20.04 on Vagrant VMs
6. No external dependencies beyond what is visible in the repository
7. Migration will maintain the same level of compliance testing
8. Existing Ansible playbooks can be preserved with minimal changes