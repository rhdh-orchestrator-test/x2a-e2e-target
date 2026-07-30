# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining InSpec tests for compliance validation

Given the limited scope (2 bash scripts for Chef deployment and 2 Ansible playbooks with InSpec tests), this migration is estimated to be a **low complexity** effort that could be completed within **1-2 weeks** by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script for Chef deployment
    - Key Features: User creation, organization setup, Chef Automate configuration

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script for Chef deployment
    - Key Features: User creation, organization setup, Chef Server configuration

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook to fix SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Create Ansible roles that configure systems according to organizational policies instead of using Chef Automate
  
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
  - Migration strategy: Use Ansible inventory and collections to manage infrastructure instead of Chef Server

- **Test Kitchen with Ansible**: Maintain but update configuration
  - Migration strategy: Update Test Kitchen configuration to work with standardized Ansible structure

- **InSpec**: Maintain as compliance testing tool
  - Migration strategy: Keep InSpec tests but integrate with Ansible workflow (e.g., using ansible_playbook provisioner)

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache
  - Migration approach: Maintain SSL configuration in Ansible playbooks, consider using Ansible Vault for certificate management
  
- **SSH Hardening**: InSpec tests verify SSH security settings
  - Migration approach: Create Ansible role for SSH hardening based on InSpec requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation strategy: Create Ansible roles that install and configure necessary packages, with variables for user/org configuration

- **InSpec Integration**: Maintaining InSpec tests with Ansible
  - Mitigation strategy: Use Ansible's built-in integration with InSpec or create a custom module/role for running InSpec tests

### Migration Order

1. **chef-and-ansible/website_https.yml** (low risk, already Ansible)
   - Standardize structure and variable naming
   - Integrate with Ansible best practices

2. **chef-and-ansible/poodle_fix.yml** (low risk, already Ansible)
   - Standardize structure and variable naming
   - Consider merging with website_https.yml as a role

3. **setup-automate/deploy-chef-server.sh** (moderate complexity)
   - Convert to Ansible playbook
   - Use Ansible Vault for credentials

4. **setup-automate/deploy-automate.sh** (moderate complexity)
   - Convert to Ansible playbook
   - Use Ansible Vault for credentials

### Assumptions

1. The repository is primarily for demonstration purposes, as indicated by the README.md mentioning "working examples" and "how-tos"
2. The Chef deployment scripts are intended for setting up Chef infrastructure, not for actual configuration management
3. The InSpec tests are meant to be used with the Ansible playbooks for compliance validation
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. The existing Ansible playbooks can be maintained with minimal changes
8. Test Kitchen is used for testing the Ansible playbooks with InSpec verification