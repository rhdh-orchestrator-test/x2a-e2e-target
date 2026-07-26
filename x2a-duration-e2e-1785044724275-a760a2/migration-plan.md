# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef setup scripts and Ansible playbooks that are used for demonstration purposes related to Chef Automate, Chef Infra Server, and Ansible integration with Chef InSpec for compliance testing. The migration scope is relatively small, focusing on:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Two Chef deployment scripts for setting up Chef Automate and Chef Infra Server
3. InSpec tests for verifying HTTPS configuration

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible. The main focus will be on replacing the Chef server deployment scripts with Ansible playbooks and ensuring the existing Ansible playbooks follow best practices.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS configuration and SSL security

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with support for both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen**: Consider migrating to Ansible Molecule for testing
- **InSpec**: Can be retained as a testing framework, as it works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configuration that must be preserved:
  - Self-signed certificate generation
  - TLS protocol version restrictions (disabling SSLv3, enabling TLSv1.2)
  - Apache SSL module configuration
  
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - SSL certificates and keys generated and stored in `/etc/apache2/certs/`
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible will require creating roles and tasks that replicate the functionality of the Chef Automate CLI
- **InSpec Integration**: Ensuring that the InSpec tests continue to work with the migrated Ansible playbooks
- **Testing Framework**: Deciding whether to keep Test Kitchen or migrate to Molecule for testing Ansible playbooks

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Organize into roles and use Ansible Vault for sensitive data

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Consider merging with website-https as they are related

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential storage
   - Develop idempotent tasks to replace the bash script functionality

4. **Testing framework** (moderate complexity)
   - Either adapt Test Kitchen configuration or migrate to Molecule
   - Ensure InSpec tests continue to work with the new setup

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md
2. The Chef deployment scripts are intended to be run on a fresh VM or server
3. The Ansible playbooks are designed to work with Ubuntu 20.04
4. The InSpec tests are an integral part of the workflow and should be preserved
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure values in a production environment
6. The repository is meant to showcase Chef and Ansible integration rather than being a complete infrastructure solution