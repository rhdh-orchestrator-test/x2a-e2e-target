# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Create Ansible roles that perform the same server setup and configuration tasks
  
- **Chef InSpec**: Maintain as a compliance testing tool
  - Migration strategy: Continue using InSpec for testing, but integrate with Ansible using the `ansible.builtin.shell` module or dedicated InSpec Ansible modules

- **Test Kitchen**: Replace with Ansible-native testing frameworks
  - Migration strategy: Use Molecule for Ansible role testing, or maintain Test Kitchen with the `kitchen-ansible` plugin

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening for Apache
  - Migration approach: Maintain the same security configurations in Ansible playbooks, ensuring TLS 1.2 is enforced

- **SSH Hardening**: InSpec tests for SSH security compliance
  - Migration approach: Create Ansible roles for SSH hardening that satisfy the InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server User Management**: The current scripts create Chef users and organizations
  - Mitigation strategy: If Chef Server is still needed, create Ansible roles that use the Chef Server API to manage users and organizations

- **InSpec Integration**: Maintaining InSpec tests within an Ansible workflow
  - Mitigation strategy: Use the `community.general.inspec` Ansible module or create a custom module for InSpec integration

### Migration Order

1. **chef-automate-deployment** (high value, moderate complexity)
   - Create Ansible playbooks to replace the bash scripts for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential storage

2. **Enhance existing Ansible playbooks** (low risk, high value)
   - Refactor existing Ansible playbooks into roles for better reusability
   - Improve variable management and templating

3. **Testing Framework** (moderate complexity)
   - Set up Molecule for Ansible role testing
   - Integrate InSpec tests with Ansible workflow

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The Chef components (Automate and Infra Server) are used for demonstration or testing purposes, not for managing a large infrastructure.

3. InSpec will continue to be used for compliance testing even after migration to Ansible.

4. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already functional and may only need refactoring rather than complete rewriting.

5. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.

6. The migration will focus on maintaining the same functionality while improving security and maintainability.