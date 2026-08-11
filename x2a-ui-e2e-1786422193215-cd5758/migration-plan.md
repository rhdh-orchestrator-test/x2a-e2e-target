# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Technologies**: Ansible playbooks, Chef InSpec tests, Bash deployment scripts

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles
- **Chef InSpec**: Two options:
  1. Convert InSpec tests to Ansible assertions using assert module
  2. Keep InSpec tests and integrate them with Ansible using the `community.general.inspec` module

- **Chef Automate/Server deployment scripts**: Convert to Ansible roles for infrastructure deployment

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
  - Migration approach: Create an Ansible role for SSL configuration with proper certificate management
  
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions may be challenging.
  - Mitigation: Consider keeping InSpec tests and integrating them with Ansible using the `community.general.inspec` module

- **Self-signed Certificate Generation**: The current playbook uses Ansible's `openssl_*` modules which have evolved over time.
  - Mitigation: Update to use the latest Ansible crypto modules and ensure idempotence

### Migration Order

1. **website_https playbook** (Priority 1): Convert to an Ansible role with proper structure
2. **poodle_fix playbook** (Priority 1): Integrate into the same Apache/SSL role
3. **InSpec tests** (Priority 2): Either convert to Ansible assertions or integrate with Ansible
4. **Chef deployment scripts** (Priority 3): Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. The InSpec tests are valuable and should be preserved in some form
3. The target environment will continue to be Ubuntu 20.04 or similar Debian-based systems
4. The deployment scripts for Chef Automate/Server may not need migration if the goal is to move away from Chef entirely
5. No external dependencies or complex data structures are used in the current implementation
6. No secrets management system is currently in place
7. The current implementation does not use any custom Ansible modules or plugins