# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with the primary focus being on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible
2. Preserving the existing Ansible playbooks that are already in place
3. Ensuring the InSpec tests continue to function with the migrated infrastructure

The migration complexity is **LOW** as most components are already Ansible-based or are simple shell scripts that can be easily converted. Estimated timeline: **1-2 weeks** for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Demonstration of using Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing or adapt to work with Ansible-only workflow.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure Apache web server. Migration consideration: Keep as-is, already in Ansible format.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Keep as-is, already in Ansible format.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Keep as-is, InSpec tests can be used with Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Keep as-is, InSpec tests can be used with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Keep as-is for compliance testing, as it works well with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible playbooks
- **Chef Automate/Infra Server**: Determine if these are still needed or if they can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The repository includes specific SSL security configurations (disabling SSLv3, enabling TLSv1.2) that must be preserved in the migration
- **SSH Security**: SSH root login restrictions are tested and should be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the Ansible playbook and should use secure key management

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible infrastructure
- **Chef Server Replacement**: If Chef Server functionality is still needed, determine how to replace it with Ansible Tower/AWX or other configuration management tools

### Migration Order

1. Convert setup scripts to Ansible playbooks (low risk, straightforward conversion)
2. Update testing framework from Test Kitchen to Ansible Molecule (moderate complexity)
3. Implement secure credential management with Ansible Vault (moderate complexity)

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use
2. The Chef InSpec tests are still valuable and should be preserved
3. The Chef Automate and Chef Infra Server deployment scripts may no longer be needed if moving entirely to Ansible
4. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't need significant changes
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure alternatives