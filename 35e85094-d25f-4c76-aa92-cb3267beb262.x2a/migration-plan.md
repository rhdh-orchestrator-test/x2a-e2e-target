# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible role-based approach while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

After thorough examination of the repository using file_search for patterns "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found. The repository primarily contains:

- Ansible playbooks (.yml files)
- Chef InSpec test files (.rb files)
- Bash deployment scripts (.sh files)

The following components require migration:

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

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
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules within playbooks
  - Option 2: Use Molecule for testing Ansible roles with testinfra as the verifier
  - Option 3: Maintain InSpec tests but integrate them with Ansible using the `inspec` Ansible module

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule for testing Ansible roles
  - Option 2: Create Ansible playbooks that handle the test environment setup

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security checks in ssh_profile.rb must be preserved
  - Convert the InSpec control to equivalent Ansible assert tasks or Molecule tests
  - Ensure root login remains disabled

- **Vault/secrets management**:
  - Current implementation uses hardcoded passwords in deploy scripts
  - Recommendation: Replace with Ansible Vault for secure credential storage
  - Credentials detected: 1 user password in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions
  - Consider using Ansible's assert module with command/shell modules to replicate InSpec functionality

- **Chef Automate Deployment**: The Chef Automate and Chef Server deployment scripts need to be converted to Ansible playbooks
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with alternative solutions

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to Ansible role structure
2. **poodle_fix.yml** (low risk, already Ansible): Convert to Ansible role structure
3. **InSpec Tests** (moderate complexity): Convert to Ansible assert tasks or Molecule tests
4. **Chef Deployment Scripts** (high complexity): Convert to Ansible roles or replace with alternative solutions

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies where possible
2. InSpec tests are valuable and their functionality should be preserved in some form
3. The deployment scripts for Chef Automate and Chef Server may no longer be needed if moving away from Chef entirely
4. The current Test Kitchen setup is used primarily for development and testing, not production deployment
5. No external Chef cookbooks or complex Chef-specific features are in use
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. The security requirements represented in the InSpec tests must be maintained in the migrated solution