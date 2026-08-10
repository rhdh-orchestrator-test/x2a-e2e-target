# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining the InSpec testing framework for compliance validation

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for validating HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for validating SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as-is for compliance testing, as it works well with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Vagrant**: Can be maintained for local testing or replaced with Docker containers in Molecule

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates that should be preserved
- **SSH Hardening**: The SSH security profile tests for root login restrictions
- **Vault/secrets management**:
  - Hardcoded credentials in Chef deployment scripts (username, password)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires:
  - Creating equivalent Ansible roles for Chef Automate installation
  - Implementing idempotent user and organization creation
  - Ensuring proper system tuning (vm.max_map_count, vm.dirty_expire_centisecs)

- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible deployment

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor website_https.yml and poodle_fix.yml into proper Ansible roles
   - Update variable handling and improve idempotence

2. **Chef Deployment Scripts** (Moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement secure credential handling with Ansible Vault

3. **Testing Framework** (Low complexity)
   - Migrate from Test Kitchen to Ansible Molecule while preserving InSpec tests
   - Create comprehensive test scenarios

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are intended to be maintained and enhanced, not replaced
2. The Chef InSpec testing framework should be preserved for compliance validation
3. The Chef Automate and Chef Infra Server deployment scripts are intended to be converted to Ansible
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The migration will maintain compatibility with Vagrant for local testing