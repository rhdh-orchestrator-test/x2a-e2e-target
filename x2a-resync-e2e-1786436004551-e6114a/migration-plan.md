# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a standardized Ansible structure
3. Preserving the Chef InSpec testing capabilities within an Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS website deployment
- `chef-and-ansible/index.html`: Unknown purpose, possibly a static file for documentation

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as a testing tool, integrated with Ansible using the `ansible_inspec` module or through CI/CD pipelines
- **Test Kitchen**: Replace with Molecule for Ansible role testing, or maintain Test Kitchen with the `kitchen-ansible` plugin

### Security Considerations

- **SSL Configuration**: The repository contains SSL hardening (POODLE fix) that must be preserved in the Ansible migration
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates; consider using Ansible's `community.crypto` collection
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate and key generation and storage
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate's architecture and dependencies
- **InSpec Integration**: Ensuring Chef InSpec tests continue to work with the new Ansible structure
- **SSL Certificate Management**: Ensuring proper handling of SSL certificates and keys in the Ansible playbooks

### Migration Order

1. **website_https and poodle_fix playbooks** (low risk, already in Ansible format)
   - Restructure into proper Ansible roles
   - Update to use Ansible best practices (variables, templates, etc.)

2. **InSpec Tests** (moderate complexity)
   - Integrate InSpec tests with Ansible using appropriate modules
   - Update test kitchen configuration or migrate to Molecule

3. **Chef Automate/Server Deployment Scripts** (high complexity)
   - Create Ansible roles to replace the bash scripts
   - Implement Ansible Vault for credential storage
   - Test thoroughly to ensure equivalent functionality

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments (based on README content)
2. The Chef InSpec tests are valuable and should be preserved in the migration
3. The hardcoded credentials in the setup scripts are for demonstration only and will be replaced with secure alternatives
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The Apache configuration and SSL requirements will remain the same in the migrated solution
6. The Chef Automate and Chef Infra Server deployment scripts are intended to be run on fresh systems
7. No external dependencies or integrations beyond what's visible in the repository