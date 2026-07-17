# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef Automate and Chef Infra Server deployment scripts, along with existing Ansible playbooks and InSpec tests. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited Chef components and existing Ansible presence.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, server configuration

- **ansible-apache-https**:
    - Description: Ansible playbook for deploying Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **ansible-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for compliance verification
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSH security compliance checks

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used in the Apache deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Can be retained as a compliance testing tool alongside Ansible

### Security Considerations

- **SSH Root Login**: InSpec tests verify SSH root login is disabled (ssh_profile.rb)
- **SSL/TLS Configuration**: 
  - Ensure TLSv1.2 is enabled and SSLv3 is disabled
  - Self-signed certificates are generated in the Ansible playbook
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate and key files
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation: Keep InSpec for compliance testing while using Ansible for configuration management
  
- **Chef Automate Functionality**: Replacing Chef Automate's functionality with Ansible equivalents
  - Mitigation: Evaluate AWX/Ansible Tower for similar dashboard and reporting capabilities

### Migration Order

1. **chef-automate-deployment** (moderate complexity)
   - Create Ansible roles to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement Ansible Vault for credential storage

2. **inspec-compliance-tests** (low complexity)
   - Retain InSpec tests but integrate with Ansible workflow
   - Update Test Kitchen configuration to work with pure Ansible

3. **ansible-apache-https** and **ansible-poodle-fix** (already in Ansible)
   - Review and optimize existing Ansible playbooks
   - Consolidate into roles for better reusability

### Assumptions

1. The repository is primarily demonstrating Chef InSpec with Ansible rather than being a production Chef deployment
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already in the target format and may not need migration
3. Test Kitchen is being used for testing Ansible playbooks with InSpec verification
4. The deployment scripts are templates/examples and not production-ready configurations
5. No complex Chef cookbooks or recipes are present in the repository
6. The primary migration need is to replace the Chef Automate and Chef Infra Server deployment with Ansible equivalents
7. InSpec will continue to be used for compliance testing even after migration to Ansible