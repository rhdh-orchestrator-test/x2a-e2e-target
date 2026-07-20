# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests as a compliance verification layer

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS deployment, SSL hardening, compliance testing

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Create Ansible roles that install and configure equivalent open-source monitoring and compliance tools
  
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
  - Migration strategy: Implement Ansible inventory management and role-based access control

- **Chef InSpec**: Maintain as a compliance testing tool
  - Migration strategy: Keep InSpec tests but integrate them with Ansible using the `inspec` Ansible module

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening (POODLE fix)
  - Migration approach: Maintain the same security hardening but implement as Ansible role
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - Migration approach: Replace with Ansible Vault for secrets management

### Technical Challenges

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem
  - Mitigation strategy: Evaluate open-source alternatives like AWX/Tower, Prometheus, and Grafana

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible-managed systems
  - Mitigation strategy: Use the Ansible `inspec` module to run tests as part of playbooks

### Migration Order

1. **chef-and-ansible/website_https.yml** (low risk, already Ansible): Standardize and optimize existing Ansible playbook
2. **chef-and-ansible/poodle_fix.yml** (low risk, already Ansible): Standardize and optimize existing Ansible playbook
3. **setup-automate** (moderate complexity): Convert bash scripts to Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The InSpec tests are intended to be maintained as the compliance verification layer
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. The migration will maintain the same functionality but standardize on Ansible
7. No actual Chef cookbooks or recipes need migration, only the deployment scripts