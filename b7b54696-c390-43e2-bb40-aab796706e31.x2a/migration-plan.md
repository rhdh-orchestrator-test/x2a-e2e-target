# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of Chef Automate and Chef Infra Server deployment scripts, along with some existing Ansible playbooks and InSpec tests. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: User creation, organization setup, server configuration

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and InSpec tests for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible and InSpec
    - Key Features: HTTPS website configuration, SSL vulnerability remediation, compliance testing

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring a secure website with Apache
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Can be retained as a compliance testing tool alongside Ansible

### Security Considerations

- **SSH Root Login**: InSpec tests verify SSH root login is disabled (ssh_profile.rb)
- **SSL/TLS Configuration**: Ensure proper TLS protocols are enabled (poodle_fix.yml)
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates and keys in Apache configuration
  - Recommend using Ansible Vault for credential storage

### Technical Challenges

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible roles that can perform equivalent user and organization creation
- **InSpec Integration**: Ensure continued integration between Ansible and InSpec for compliance testing
- **SSL Certificate Management**: Ensure proper handling of SSL certificates in the Ansible playbooks

### Migration Order

1. **chef-automate-deployment** (high value, moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement secure credential handling with Ansible Vault

2. **Existing Ansible Playbooks** (low risk, low complexity)
   - Review and optimize existing Ansible playbooks (website_https.yml, poodle_fix.yml)
   - Ensure they follow best practices and are properly documented

3. **InSpec Tests** (low complexity)
   - Retain InSpec tests for compliance verification
   - Ensure proper integration with Ansible playbooks

### Assumptions

1. The repository is primarily focused on demonstrating Chef InSpec with Ansible rather than being a production deployment
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already in a format that can be used directly
3. The Chef deployment scripts are the primary targets for migration to Ansible
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 as specified in kitchen.yml
6. The InSpec tests will continue to be used for compliance verification after migration
7. No external Chef cookbooks or recipes are being used that would need migration