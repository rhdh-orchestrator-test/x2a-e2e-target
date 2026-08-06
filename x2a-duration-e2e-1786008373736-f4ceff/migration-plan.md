# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Chef Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Migrating Chef InSpec tests to Ansible-compatible testing frameworks

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains deployment scripts and simple Ansible playbooks with InSpec tests

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

No traditional modules (Puppet modules with manifests/init.pp, Chef cookbooks with recipes/default.rb, or PowerShell modules with .psd1 files) were found in this repository. The repository contains:

- Ansible playbooks in the chef-and-ansible directory
- Bash deployment scripts in the setup-automate directory
- InSpec test files in the chef-and-ansible/tests directory

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys a simple HTTPS website with Apache2 and self-signed certificates
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Likely a sample HTML file for testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - ansible-lint for static analysis
  - Molecule for testing Ansible roles
  - testinfra for infrastructure testing (Python-based alternative to InSpec)
  - Or maintain InSpec as a standalone testing tool that works with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration must maintain secure SSL settings:
  - Disabling SSLv3 (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - Proper certificate generation and management

- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration must maintain this security control.

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the Chef deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef Automate and Chef Infra Server installation
  - Implementing idempotent installation checks
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)

- **Testing Framework Migration**: Moving from InSpec to Ansible-native testing:
  - Converting Ruby-based InSpec tests to Python-based testinfra or maintaining InSpec
  - Ensuring compliance checks remain accurate and comprehensive

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already Ansible)
   - Standardize and optimize existing website_https.yml and poodle_fix.yml playbooks
   - Convert to roles for better reusability

2. **Chef Deployment Scripts** (Medium complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement variable handling with Ansible Vault for credentials

3. **Testing Framework** (Medium complexity)
   - Decide whether to maintain InSpec or migrate to Ansible-native testing
   - Convert tests if necessary

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The Chef deployment scripts are intended for on-premises or generic cloud VMs
3. The hardcoded credentials in the deployment scripts are examples and not used in production
4. The InSpec tests are meant to demonstrate compliance automation alongside Ansible
5. The existing Ansible playbooks are functional but may not follow best practices
6. No complex Chef cookbooks or recipes need migration (none were found in the repository)