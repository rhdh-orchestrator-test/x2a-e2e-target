# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates SSL vulnerabilities by disabling older protocols
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS configuration, SSL security, and SSH compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL protocol security checks, SSH security verification

- **chef-deployment-scripts**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Shell Script
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in assert module for basic tests and ansible-lint for static analysis. For more complex compliance testing, consider:
  - Option 1: Use community.general.inspec module to continue running InSpec tests from Ansible
  - Option 2: Migrate tests to Ansible's assert module where possible
  - Option 3: Implement compliance testing with OpenSCAP and ansible-lockdown

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and job scheduling
  - Ansible Content Collections for role and playbook management
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in poodle_fix.yml
  - Approach: Create an Ansible role for SSL hardening that implements the same security controls

- **SSH Security**: The SSH compliance checks must be maintained
  - Approach: Create an Ansible role that configures SSH according to the same security standards and implements verification

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing capabilities currently provided by InSpec
  - Mitigation: Use the community.general.inspec Ansible module to continue running existing InSpec tests, while gradually migrating to native Ansible testing methods

- **Chef Automate Functionality**: Chef Automate provides compliance reporting that needs an equivalent in the Ansible ecosystem
  - Mitigation: Implement AWX/Ansible Tower with compliance reporting plugins or integrate with a dedicated compliance tool like OpenSCAP

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role with variables

2. **poodle-ssl-fix** (low risk, already in Ansible)
   - Integrate into the HTTPS configuration role as a security hardening task

3. **inspec-compliance-tests** (moderate complexity)
   - Initially keep as InSpec tests run via the community.general.inspec module
   - Gradually migrate to Ansible assert statements where possible

4. **chef-deployment-scripts** (high complexity)
   - Replace with AWX/Ansible Tower deployment
   - Implement equivalent user and organization management in Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation, not to provide production-ready infrastructure
2. The InSpec tests are the most valuable components to preserve in the migration
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. The migration will consolidate all infrastructure provisioning into Ansible while maintaining the same level of compliance testing
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure credential management
6. The self-signed certificates are acceptable for the demonstration environment but would be replaced with proper certificates in production