# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef Automate deployment scripts that need to be migrated to a standardized Ansible format. The repository appears to be a demonstration of using Chef InSpec with Ansible for compliance automation, rather than a full Chef cookbook repository. The migration scope is relatively small, focusing on:

1. Standardizing existing Ansible playbooks
2. Converting Chef Automate deployment scripts to Ansible playbooks
3. Preserving InSpec tests for compliance validation

Given the limited scope, this migration is estimated to be **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS**.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, disabling SSLv3

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec Tests**: Preserve InSpec tests for compliance validation, integrate with Ansible using ansible_inspec module or Molecule verifier
- **Chef Automate/Server Deployment**: Convert bash scripts to Ansible playbooks that install and configure Chef components

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper certificate management in the migrated Ansible roles.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Ensure SSH hardening is included in the migrated Ansible roles.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates in website_https.yml
  - Recommend using Ansible Vault for credential storage in the migrated solution

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible roles may require additional configuration.
- **Chef Automate Installation**: Converting the Chef Automate installation scripts to idempotent Ansible playbooks will require careful handling of installation states.
- **Testing Framework**: Replacing Test Kitchen with Molecule will require new test configurations.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Standardize to Ansible role structure
   - Integrate with Molecule testing
   - Preserve InSpec tests

2. **poodle_fix playbook** (low risk, already Ansible)
   - Standardize to Ansible role structure
   - Integrate with Molecule testing
   - Preserve InSpec tests

3. **Chef deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement idempotency checks
   - Use Ansible Vault for credentials

### Assumptions

1. The repository is primarily a demonstration of using Chef InSpec with Ansible rather than a production infrastructure codebase.
2. The InSpec tests should be preserved as they provide valuable compliance validation.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The Chef Automate and Chef Server deployment scripts are intended for development/testing environments, not production, given the hardcoded credentials.
5. The migration goal is to standardize on Ansible while preserving the compliance testing capabilities of InSpec.