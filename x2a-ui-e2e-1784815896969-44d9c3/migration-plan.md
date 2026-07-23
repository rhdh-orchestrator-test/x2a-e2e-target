# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/org creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration against POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible's built-in assert module where appropriate
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that accomplish the same server setup

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests validate SSH security configurations.
  - Migration approach: Implement SSH hardening using Ansible's `lineinfile` or templates, maintain InSpec tests

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests from Ansible

- **Chef Automate Deployment**: Converting Chef Automate deployment to Ansible
  - Mitigation: Create Ansible roles that download and configure Chef components using the official installation methods

### Migration Order

1. **setup-automate scripts** (Priority 1): Convert bash scripts to Ansible playbooks
   - Create roles for Chef Automate and Chef Infra Server deployment
   - Use Ansible Vault for credential storage

2. **chef-and-ansible playbooks** (Priority 2): Standardize existing Ansible playbooks
   - Refactor into proper roles and playbooks following Ansible best practices
   - Maintain compatibility with existing InSpec tests

3. **InSpec tests** (Priority 3): Integrate InSpec tests with Ansible
   - Use Ansible's InSpec module or consider migrating to native Ansible assertions

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The Chef Automate/Infra Server deployment is intended for testing or development environments
3. The hardcoded credentials in the scripts are not used in production environments
4. The InSpec tests are valuable and should be maintained rather than replaced
5. The target environment will continue to be Ubuntu 20.04 or similar
6. The Apache configuration is relatively simple and can be directly translated to Ansible
7. No complex Chef-specific features are being used that would be difficult to replicate in Ansible