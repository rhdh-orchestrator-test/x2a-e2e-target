# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

[This migration plan outlines the process of converting Chef InSpec tests to Ansible-native testing solutions while preserving existing Ansible playbooks.]

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks and InSpec tests for HTTPS website deployment and compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache web server with HTTPS, SSL security configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache
- `chef-and-ansible/index.html`: Sample HTML content for the web server
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for HTTPS functionality
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule with testinfra for testing
  - **Option 2**: Use community.general.assert module for basic compliance checks
  - **Option 3**: Integrate with other compliance tools like OSCAP or Lynis

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the Apache SSL configuration maintains TLSv1.2 requirement
  
- **SSH Security**: The SSH compliance checks in ssh_profile.rb must be preserved
  - Approach: Convert InSpec tests to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - Hardcoded credentials found in setup-automate scripts should be migrated to Ansible Vault:
    - Username, password, and email credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Molecule with testinfra which has similar syntax to InSpec
  
- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles
  - Mitigation: Create dedicated Ansible roles for Chef Automate and Chef Server deployment

### Migration Order

1. **chef-and-ansible/website_https.yml** (already in Ansible, no migration needed)
2. **chef-and-ansible/poodle_fix.yml** (already in Ansible, no migration needed)
3. **chef-and-ansible/tests/website_https_verify.rb** (convert InSpec tests to Ansible Molecule/testinfra)
4. **chef-and-ansible/tests/ssh_profile.rb** (convert InSpec compliance profile to Ansible checks)
5. **setup-automate/deploy-automate.sh** and **setup-automate/deploy-chef-server.sh** (convert to Ansible roles)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements will remain the same
5. The repository is primarily for demonstration purposes rather than production use
6. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
7. The hardcoded credentials in the setup scripts are for demonstration purposes only