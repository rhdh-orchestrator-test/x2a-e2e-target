# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with well-defined functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible-native testing solutions like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an Apache web server with HTTPS. This can remain as-is but should be integrated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. This can remain as-is but should be integrated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS configuration. Should be migrated to Ansible-native testing or integrated with Ansible using ansible-test.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for SSH security compliance. Should be migrated to Ansible-native testing or integrated with Ansible using ansible-test.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in the Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static code analysis
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Maintain InSpec as a separate testing tool but invoke it through Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. Migration should maintain or enhance these security settings.
  - Migration approach: Preserve the same SSL/TLS configurations in the new Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration should maintain this security check.
  - Migration approach: Convert InSpec tests to Ansible assertions or maintain as separate compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - Migration approach: Replace hardcoded credentials with Ansible Vault or external secret management solution

### Technical Challenges

- **Chef InSpec Testing**: The repository uses Chef InSpec for compliance testing. 
  - Mitigation: Either maintain InSpec as a separate tool or migrate tests to Ansible-native solutions like ansible-test or Molecule

- **Test Kitchen Integration**: The repository uses Test Kitchen for testing Ansible playbooks.
  - Mitigation: Replace Test Kitchen with Molecule for testing Ansible roles and playbooks

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to the new Ansible structure
   - Update any deprecated syntax or modules

2. **Chef Deployment Scripts** (Medium complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Replace hardcoded credentials with Ansible Vault

3. **Testing Framework** (Medium complexity)
   - Migrate from Test Kitchen to Molecule
   - Either integrate InSpec tests with Ansible or convert to Ansible-native testing

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The security requirements (TLS 1.2, SSH hardening) will remain the same
4. The Chef Automate and Chef Infra Server deployment scripts are being migrated because the organization is moving away from Chef to Ansible
5. The existing Ansible playbooks are functional and follow best practices
6. The InSpec tests are comprehensive and should be preserved in some form
7. No additional functionality beyond what exists in the current scripts is required