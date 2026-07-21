# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec compliance testing functionality within the Ansible ecosystem

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no Puppet modules (`**/manifests/init.pp`), Chef cookbooks (`**/recipes/default.rb`), or PowerShell modules (`**/*.psd1`) in this repository. The file searches returned no results for these patterns.

The repository contains:

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec Tests**: Maintain InSpec tests but integrate with Ansible using the ansible_inspec module or convert to Ansible-native testing with Molecule
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source AWX for centralized automation management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert to an Ansible role with appropriate variables for SSL protocols
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules (already in use) in a standardized role

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Migration approach: Create an Ansible role for SSH hardening that implements the controls tested by the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Maintaining compliance testing while migrating to pure Ansible
  - Mitigation: Use Ansible's built-in assert module for basic tests and maintain InSpec for complex compliance testing
  
- **Chef Server Functionality**: Replacing Chef Server's node management capabilities
  - Mitigation: Implement Ansible inventory management with dynamic inventories and AWX/Ansible Tower

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure with variables
   - Maintain InSpec tests

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Could be combined with website_https as a security enhancement role

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible playbooks to deploy Ansible Automation Platform or AWX
   - Implement user/organization management in Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating it's for "examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The InSpec tests are essential to maintain as they demonstrate compliance automation capabilities.

3. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with equivalent Ansible Automation Platform or AWX deployment capabilities.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with proper secret management in production.

5. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration, but the solution should be adaptable to other Linux distributions.