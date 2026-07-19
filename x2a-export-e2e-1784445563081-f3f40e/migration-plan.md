# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks with minor improvements
3. Maintaining Chef InSpec for compliance testing while integrating it with Ansible

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most functionality already in Ansible

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS website verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Maintain as a compliance testing tool, integrate with Ansible using the `ansible.builtin.shell` module or dedicated Ansible collection

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (poodle_fix.yml) which should be preserved in the migrated solution
- **SSH Hardening**: InSpec tests for SSH security should be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates in the Ansible playbook
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Ensure InSpec tests continue to work with pure Ansible deployment
  - Mitigation: Use the `community.general.inspec` Ansible module or create a custom role
  
- **Configuration Management**: Replace Chef Automate/Infra Server with alternative configuration management
  - Mitigation: Use AWX/Ansible Tower or other Ansible-based configuration management solutions

### Migration Order

1. **chef-and-ansible module** (low risk, already Ansible)
   - Refactor existing Ansible playbooks to use best practices
   - Integrate InSpec tests with Ansible using the community.general.inspec module
   - Replace Test Kitchen with Ansible Molecule

2. **setup-automate module** (moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Replace Chef Automate/Infra Server with AWX/Ansible Tower or other Ansible-based solution
   - Implement Ansible Vault for secure credential storage

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, not to provide production-ready code
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
3. The target environment will continue to be Ubuntu 20.04 or similar
4. InSpec will remain the compliance testing tool of choice
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The migration will maintain the same level of security hardening present in the original code
7. The deployment scripts contain default/example credentials that would be replaced in production