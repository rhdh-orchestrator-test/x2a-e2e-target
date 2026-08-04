# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

**Timeline Estimate**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for validating HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test profile for validating SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain or migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing or consider migrating to Ansible's built-in assert module

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain secure TLS settings:
  - Disabling SSLv3 protocol (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - Self-signed certificate generation

- **SSH Hardening**: InSpec tests validate SSH security configurations:
  - Root login disabled
  - SSH server configuration validation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires:
  - Creating Ansible roles for Chef Automate installation
  - Implementing idempotent installation checks
  - Managing system requirements (vm.max_map_count, vm.dirty_expire_centisecs)

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible:
  - Option 1: Keep InSpec for compliance testing
  - Option 2: Convert InSpec tests to Ansible assertions or molecule tests

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor website_https.yml and poodle_fix.yml to follow Ansible best practices
   - Convert inline templates to separate template files
   - Implement variable files instead of inline variables

2. **Chef Deployment Scripts** (Moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential storage
   - Add idempotency checks to prevent reinstallation

3. **Testing Framework** (Low complexity)
   - Maintain InSpec tests but integrate with Ansible workflow
   - Consider migrating Test Kitchen configuration to Molecule

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.
2. The Chef Automate and Chef Server deployment scripts are intended for on-premises or cloud VM deployment.
3. The hardcoded credentials in the deployment scripts are examples and not production credentials.
4. The InSpec tests are intended to be run as part of the Test Kitchen workflow.
5. The existing Ansible playbooks are functional and follow basic Ansible practices but could benefit from refactoring.