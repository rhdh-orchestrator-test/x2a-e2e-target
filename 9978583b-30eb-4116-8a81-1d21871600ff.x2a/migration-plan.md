# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on infrastructure automation and compliance testing. The primary migration scope involves:

1. Chef Automate and Chef Infra Server deployment scripts
2. Chef InSpec compliance tests that are already being used with Ansible playbooks

The migration complexity is relatively low as most components are already Ansible-based or are simple deployment scripts. The estimated timeline for migration is 1-2 weeks, primarily focusing on converting the Chef server deployment scripts to Ansible playbooks and ensuring the InSpec tests continue to work properly with the migrated infrastructure.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with InSpec testing for Apache HTTPS deployment
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, Chef server configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/index.html`: Sample HTML file used in the Apache deployment example
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only
- `README.md`: Repository documentation files

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Keep using InSpec for compliance testing with Ansible as it's already integrated and working
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or another Ansible-based management solution
- **Test Kitchen with Ansible**: Continue using Test Kitchen for testing Ansible playbooks

### Security Considerations

- **SSH Root Login**: The InSpec tests verify SSH root login is disabled; ensure this security check is maintained
- **SSL/TLS Configuration**: The playbooks configure SSL certificates and disable vulnerable protocols; maintain these security practices
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbooks; consider using Ansible Vault for storing pre-generated certificates
  - Count of credentials detected: 4 (username, password, email, organization name in deployment scripts)

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks will require understanding of Chef server architecture
- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated infrastructure
- **Test Kitchen Configuration**: Updating Test Kitchen configuration if needed for the new Ansible structure

### Migration Order

1. **chef-and-ansible** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks (website_https.yml and poodle_fix.yml)
   - Ensure they follow best practices and use Ansible Vault for sensitive data
   - Maintain InSpec test integration

2. **setup-automate** (moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Use Ansible Vault for credentials
   - Test deployment thoroughly

### Assumptions

1. The repository is primarily used for demonstration and educational purposes rather than production deployment
2. The InSpec tests are intended to be used with Ansible playbooks as shown in the kitchen.yml configuration
3. The Chef server deployment scripts are the main components that need migration to Ansible
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external Chef cookbooks or complex Chef recipes are present in the repository
6. The migration will maintain the same security testing and compliance verification capabilities
7. Test Kitchen will continue to be used for testing the migrated Ansible playbooks