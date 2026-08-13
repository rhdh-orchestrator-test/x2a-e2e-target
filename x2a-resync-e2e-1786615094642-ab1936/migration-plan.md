# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily for demonstration purposes rather than a full production infrastructure codebase.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features
  - GitLab CI/GitHub Actions for pipeline integration

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Secure virtual host configuration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Root login restrictions
  - SSH protocol security settings
  - These tests should be converted to Ansible assertions or molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec has a different testing syntax and approach than Ansible's assert module
  - Solution: Use Ansible's assert module or molecule verify phase with testinfra

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management:
  - The current scripts deploy Chef Automate and Chef Infra Server
  - Solution: Create Ansible roles for AWX/Tower deployment or use containerized deployment with Docker/Kubernetes

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, already in Ansible format
   - Only need formatting and organization into proper roles/collections

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb):
   - Moderate complexity
   - Convert to Ansible assert tasks or molecule tests

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Higher complexity
   - Create Ansible roles for AWX/Tower deployment

### Assumptions

1. The repository is primarily for demonstration purposes, not a production infrastructure
2. The InSpec tests are used for compliance verification of systems managed by Ansible
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
4. No external dependencies or modules are required beyond what's visible in the repository
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No complex data structures or variable hierarchies are in use
7. No external inventory or host management system is referenced
8. No secrets management system is currently in use (passwords are hardcoded)