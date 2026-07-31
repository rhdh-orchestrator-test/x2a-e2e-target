# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec testing capabilities within an Ansible workflow

Based on the repository analysis, this is a low-complexity migration that should take approximately 1-2 weeks to complete, with most of the effort focused on properly structuring the Ansible roles and integrating the InSpec testing framework.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Apache web server configuration with SSL/TLS setup, virtual host configuration, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Security fix for the POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script for Chef deployment
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Deployment script for Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script for Chef deployment
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt Test Kitchen to work with pure Ansible
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the ansible_inspec module or Molecule verifier
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or another Ansible management platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 requirement and disabled SSLv3 as implemented in the poodle_fix.yml playbook
- **SSH Hardening**: Maintain compliance with the SSH security profile that disables root login
- **Vault/secrets management**:
  - Credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, possibly using ansible-vault or an external secrets manager

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible roles
  - Mitigation: Use the ansible_inspec module or Molecule with InSpec verifier
  
- **Chef Server Replacement**: Determining if Chef Server functionality needs to be replaced with Ansible Tower/AWX
  - Mitigation: Evaluate if centralized configuration management is needed or if ad-hoc Ansible usage is sufficient

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Restructure into proper Ansible role format
   - Integrate with InSpec tests

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Restructure into proper Ansible role format
   - Could be merged with the website_https role as a security enhancement

3. **Chef deployment scripts** (moderate complexity)
   - Convert to Ansible playbooks for deploying management infrastructure
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production infrastructure codebase
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
3. The existing Ansible playbooks are examples rather than production code
4. The migration goal is to standardize on Ansible while maintaining InSpec for compliance testing
5. No external Chef cookbooks or complex Chef-specific functionality needs to be migrated