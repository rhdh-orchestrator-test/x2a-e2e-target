# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and shell scripts focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring a secure HTTPS website
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example repository demonstrating Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS website configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests that verify HTTPS configuration and security
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile that verifies SSH security configuration
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with:
  - Option 1: molecule for Ansible role/playbook testing
  - Option 2: ansible-test for collection testing

- **Chef Automate/Server**: Replace with:
  - Ansible Automation Platform for centralized automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate handlers and idempotent tasks

- **SSH Security**: The SSH compliance checks must be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the playbook
  - Approach: Use Ansible Vault for credential storage and ansible.builtin.expect for interactive prompts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Create custom Ansible modules or use assert tasks with appropriate register variables

- **Compliance Reporting**: Maintaining compliance reporting capabilities without Chef InSpec
  - Mitigation: Integrate with Ansible Automation Platform's compliance features or export test results in a standardized format

- **Certificate Management**: Ensuring proper certificate generation and management
  - Mitigation: Use the ansible.builtin.openssl_* modules consistently with proper error handling

### Migration Order

1. **Website HTTPS Configuration** (low risk, already in Ansible)
   - Convert website_https.yml to a proper Ansible role with variables
   - Improve idempotence of commands

2. **POODLE Vulnerability Fix** (low risk, already in Ansible)
   - Integrate poodle_fix.yml into the website HTTPS role as a configurable option
   - Ensure handlers are properly organized

3. **Chef Automate/Server Deployment Scripts** (moderate complexity)
   - Convert shell scripts to Ansible playbooks
   - Use Ansible Vault for credential storage

4. **InSpec Compliance Tests** (high complexity)
   - Convert InSpec tests to Ansible assert tasks or custom modules
   - Ensure equivalent coverage and reporting

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The migration will standardize on Ansible completely, removing Chef components
4. Test Kitchen is used primarily for development testing, not production deployment
5. The hardcoded credentials in the setup scripts are for demonstration purposes only
6. The self-signed certificates are acceptable for the demonstration environment
7. The compliance tests are meant to demonstrate capability rather than enforce specific organizational policies