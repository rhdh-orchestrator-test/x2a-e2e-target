# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while enhancing them with best practices
3. Maintaining Chef InSpec testing capabilities within the Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing for deploying and securing a web server
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS-enabled Apache web server
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration against POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate with Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrating with Ansible using the `ansible.builtin.shell` module or Ansible's built-in `assert` module
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Vagrant**: Continue using Vagrant for local development and testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in `poodle_fix.yml`
- **SSH Hardening**: Maintain the SSH security controls verified by `ssh_profile.rb`
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Self-signed SSL certificates in `website_https.yml`
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring Chef InSpec tests continue to work with Ansible-managed infrastructure
  - Solution: Use Ansible's `community.general.inspec` module or call InSpec directly via the `ansible.builtin.shell` module
  
- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Solution: Create Ansible roles for Chef Automate and Chef Infra Server deployment with idempotent tasks

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor existing Ansible playbooks to follow best practices
   - Convert to roles for better organization
   - Implement Ansible Vault for secrets

2. **Chef Deployment Scripts** (Moderate complexity)
   - Convert bash scripts to Ansible roles
   - Implement idempotent deployment tasks
   - Use Ansible Vault for credentials

3. **Testing Framework** (Moderate complexity)
   - Migrate from Test Kitchen to Molecule
   - Preserve InSpec tests and integrate with Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README.md content.
2. The Chef InSpec tests are intended to be maintained as part of the compliance strategy.
3. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure alternatives.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The Apache configuration is intended to be a simple example and may need enhancement for production use.
6. The repository does not contain actual Chef cookbooks, only Chef Automate deployment scripts and InSpec tests.