# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstration and example purposes. The primary content consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Shell scripts for deploying Chef Automate and Chef Infra Server
3. InSpec tests for verifying HTTPS configuration

The migration scope is relatively small, with only a few Ansible playbooks that need to be updated to current best practices and shell scripts that need to be converted to Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Can be retained for compliance testing with Ansible, or migrated to Ansible-native testing frameworks

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security settings:
  - Current configuration enforces TLSv1.2 and disables SSLv3 (POODLE mitigation)
  - Self-signed certificates are generated using OpenSSL
  - Migration should update to modern TLS standards (TLS 1.3 where possible)

- **Hardcoded Credentials**: The Chef server deployment scripts contain hardcoded credentials:
  - Username, password, and email in deploy-automate.sh and deploy-chef-server.sh
  - These should be moved to Ansible Vault or other secure storage in the migration

- **Vault/secrets management**:
  - No existing vault implementation detected
  - 2 credential sets identified in the Chef server deployment scripts

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef server installation
  - Implementing idempotent checks for installation status
  - Managing Chef user and organization creation through Ansible

- **InSpec Integration**: Maintaining the compliance testing capabilities while migrating to Ansible:
  - Option 1: Keep InSpec tests and integrate with Ansible workflows
  - Option 2: Convert InSpec tests to Ansible-native testing frameworks

### Migration Order

1. **website_https playbook** (low risk, already Ansible): Update to current Ansible best practices
2. **poodle_fix playbook** (low risk, already Ansible): Update to current Ansible best practices
3. **chef-server-deploy script** (moderate complexity): Convert to Ansible playbook
4. **chef-automate-deploy script** (moderate complexity): Convert to Ansible playbook

### Assumptions

1. The repository is primarily for demonstration purposes and not production use, based on the README content.
2. The InSpec tests are intended to be used alongside Ansible for compliance verification.
3. The hardcoded credentials in the Chef deployment scripts are for demonstration only.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The Apache configuration is basic and doesn't include complex customizations.
6. There are no external dependencies or integrations beyond what's visible in the repository.
7. The migration goal is to standardize on Ansible while maintaining the compliance testing capabilities.