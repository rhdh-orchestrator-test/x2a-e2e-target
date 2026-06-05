# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec test profiles that need to be preserved or migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks

The migration complexity is **LOW** as most of the repository already contains Ansible playbooks. The estimated timeline for migration is **1-2 weeks** for a single developer, primarily focused on converting the Chef server deployment scripts to Ansible and ensuring the InSpec tests continue to work with the migrated infrastructure.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec compliance tests for validating HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL/TLS protocol verification, SSH root login security check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, Chef server configuration

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS enabled. No migration needed as it's already in Ansible format.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration to mitigate POODLE vulnerability. No migration needed as it's already in Ansible format.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use pure Ansible testing approach.
- `chef-and-ansible/index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule for Ansible role testing
  - Option 2: Create custom Ansible playbooks for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in `poodle_fix.yml` that disables SSLv3 and only enables TLSv1.2
- **SSH Security**: The InSpec profile `ssh_profile.rb` checks for secure SSH configuration (disabling root login). This security check must be preserved in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Self-signed certificates generated in the `website_https.yml` playbook
  - Recommend using Ansible Vault to secure these credentials in the migrated solution

### Technical Challenges

- **InSpec Test Integration**: Determining the best approach to maintain compliance testing while moving away from Chef InSpec. Mitigation: Evaluate Ansible's native assertion capabilities or consider keeping InSpec as a standalone tool called from Ansible.
- **Chef Server Replacement**: The current setup deploys Chef Server for infrastructure management. Mitigation: Design an equivalent Ansible Control Node setup with proper inventory management to replace Chef Server functionality.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - No changes needed for `website_https.yml` and `poodle_fix.yml`

2. **Chef Server Deployment Scripts** (Medium complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Implement proper secret management using Ansible Vault

3. **InSpec Tests** (Medium complexity)
   - Evaluate options for maintaining compliance testing
   - Either convert InSpec tests to Ansible assertions or create a workflow to continue using InSpec with Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The current setup uses Test Kitchen with Vagrant for local testing, which may need to be replaced with an Ansible-native testing framework.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
4. The target environment is Ubuntu 20.04, as specified in the kitchen.yml file.
5. The repository is primarily educational/demonstrative rather than production infrastructure code.
6. The InSpec tests are considered valuable and should be preserved in some form rather than discarded.