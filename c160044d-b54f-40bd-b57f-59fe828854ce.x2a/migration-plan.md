# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating compliance automation with Chef InSpec alongside Ansible playbooks. The repository is relatively small and appears to be primarily for demonstration purposes rather than a full production infrastructure codebase.

The migration scope is limited, as most of the content is already in Ansible format. The primary migration effort will involve:
1. Converting the Chef Automate and Chef Server deployment scripts to Ansible playbooks
2. Ensuring the InSpec tests are properly integrated with Ansible workflows
3. Standardizing the existing Ansible playbooks to follow best practices

Given the small size and demonstration nature of the repository, the estimated timeline for migration is 1-2 weeks with a single engineer.

## Module Migration Plan

This repository contains a mix of Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User and organization creation, Chef Automate and Chef Infra Server installation

- **website-https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec-tests**:
    - Description: Chef InSpec tests for verifying SSH security and HTTPS website functionality
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS port and protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy only Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml and targeted by Apache package versions)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec tests but integrate them with Ansible using the `ansible.builtin.command` or `community.general.inspec` module
- **Chef Automate/Server**: Replace deployment scripts with Ansible roles for Chef server deployment, or consider migrating to AWX/Ansible Tower for similar functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. This security check should be maintained in the Ansible migration.
- **Secrets Management**: 
  - Hardcoded credentials in the Chef deployment scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible workflows without Test Kitchen
  - Mitigation: Use the Ansible `verify` module or create a dedicated role for running InSpec tests
  
- **Chef Server Deployment**: Deciding whether to maintain Chef Server deployment or replace it with Ansible Tower/AWX
  - Mitigation: Create an Ansible role that can optionally deploy Chef Server for organizations that still need it, or provide migration path to AWX

### Migration Order

1. **chef-and-ansible/poodle_fix.yml** (already in Ansible format, just needs standardization)
2. **chef-and-ansible/website_https.yml** (already in Ansible format, just needs standardization)
3. **setup-automate** scripts (convert to Ansible roles)
4. **chef-and-ansible/tests** (integrate InSpec tests with Ansible)

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The organization wants to maintain InSpec for compliance testing while standardizing on Ansible for configuration management
4. The Chef Automate and Chef Server deployment might still be needed in some form
5. No external Chef cookbooks or complex Chef-specific features are in use
6. The migration is focused on standardizing on Ansible rather than replacing functionality