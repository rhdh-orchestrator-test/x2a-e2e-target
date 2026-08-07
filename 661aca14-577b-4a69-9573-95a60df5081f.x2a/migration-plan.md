# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that are already in place
3. Ensuring Chef InSpec tests continue to work with the migrated Ansible infrastructure

The migration complexity is **LOW** as most of the repository already uses Ansible playbooks with InSpec tests. The estimated timeline for migration is **1-2 weeks** for a single developer, primarily focused on converting the Chef server deployment scripts to Ansible and ensuring proper integration with existing InSpec tests.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain as is, but update configuration if needed
- **InSpec**: Maintain as is for compliance testing with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL security configurations in the Apache setup
  - Approach: Ensure Ansible playbooks maintain the same SSL protocol restrictions (TLSv1.2)
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Approach: Ensure Ansible playbooks configure SSH with the same security parameters

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server User Management**: The current scripts create Chef users and organizations
  - Mitigation: Create Ansible roles that manage system users and groups directly

- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible infrastructure
  - Mitigation: Maintain the same file paths and configurations that InSpec tests are verifying

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** scripts (high priority, requires complete rewrite)
   - Convert to Ansible roles and playbooks
   - Implement Ansible Vault for credential storage
   - Test deployment on Ubuntu 20.04

2. **Existing Ansible Playbooks** (low risk, minimal changes)
   - Review and update as needed
   - Ensure compatibility with new Ansible roles
   - Maintain InSpec test compatibility

3. **Test Kitchen Configuration** (low risk, minimal changes)
   - Update to work with new Ansible roles and playbooks
   - Ensure InSpec tests continue to pass

### Assumptions

1. The primary goal is to eliminate Chef server/client dependencies while maintaining InSpec for compliance testing
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need significant changes
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. The InSpec tests should continue to work without modification
5. The Chef Automate and Chef Server deployment scripts are the main focus of the migration
6. No external Chef cookbooks or recipes are being used beyond what's visible in the repository
7. The organization structure and user management currently handled by Chef will be replaced with direct system management via Ansible