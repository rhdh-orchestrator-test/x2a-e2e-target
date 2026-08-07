# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, rather than containing actual Chef cookbooks. The migration scope is relatively small, focusing on:

1. Ansible playbooks that set up a secure web server with SSL
2. Chef InSpec tests for validating the web server configuration
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate and test all components. The main effort will be in ensuring that the Chef InSpec tests continue to work with the migrated Ansible playbooks and creating Ansible roles to replace the Chef server deployment scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: Chef InSpec test file for validating HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **chef-automate CLI**: Replace with Ansible roles for Chef Automate deployment
- **chef-server-ctl**: Replace with Ansible modules for managing Chef Server configuration
- **Test Kitchen**: Consider migrating to Ansible Molecule for testing
- **InSpec**: Retain InSpec for compliance testing, but integrate with Ansible workflow

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols. This security practice should be maintained in the migrated solution.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider adding support for Let's Encrypt in the migrated solution.
- **Vault/secrets management**: 
  - Hardcoded credentials in the deployment scripts (username, password)
  - SSL certificate and key files
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec Integration**: Ensuring that Chef InSpec tests continue to work with the migrated Ansible playbooks
- **Chef Server Deployment**: Creating Ansible roles to replace the Chef server deployment scripts
- **Testing Framework**: Migrating from Test Kitchen to an Ansible-native testing framework

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Add variable parameterization
   - Improve idempotence

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Consider merging with website_https role as a security feature

3. **InSpec tests** (moderate complexity)
   - Integrate with Ansible testing workflow
   - Ensure tests work with migrated roles

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to maintain the functionality of the Ansible playbooks and InSpec tests, while converting the Chef deployment scripts to Ansible.
2. The InSpec tests will continue to be used for compliance validation.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The repository is primarily for demonstration purposes rather than production use.