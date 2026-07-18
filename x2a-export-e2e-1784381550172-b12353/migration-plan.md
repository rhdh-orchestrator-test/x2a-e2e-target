# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for web server configuration with InSpec tests for compliance verification
3. Test Kitchen configuration for integration testing

The migration complexity is relatively low as most of the actual infrastructure configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests continue to work with the pure Ansible solution.

Estimated timeline: 1-2 weeks for a complete migration, with most of the effort focused on replacing the Chef server deployment scripts and ensuring compliance testing integration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for integration testing - will need to be updated to use Ansible-only testing approach
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website - can be kept with minimal changes
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability - can be kept with minimal changes
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website - can be kept as is for compliance testing
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance - can be kept as is for compliance testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate - needs to be replaced with Ansible playbook
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server - needs to be replaced with Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for compliance management
- **Chef InSpec**: Can be retained as a compliance testing tool, but integrated with Ansible workflows
- **Test Kitchen**: Replace with Ansible-native testing tools like Molecule, or adapt to use with pure Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for web servers, which needs to be preserved in the migration
  - Migration approach: Keep existing SSL configuration in Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH security configurations
  - Migration approach: Keep InSpec tests for compliance verification, integrate with Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) - should be moved to Ansible Vault
  - SSL certificates are generated dynamically - this approach can be maintained

### Technical Challenges

- **Compliance Testing Integration**: Ensuring InSpec tests continue to work with pure Ansible deployments
  - Mitigation: Create an Ansible role that installs and runs InSpec tests as part of the deployment pipeline

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible for Chef Automate features
  - Mitigation: Evaluate AWX/Tower for enterprise management and compliance features

### Migration Order

1. Create Ansible roles for web server configuration (low risk, already mostly in Ansible)
2. Create Ansible playbooks to replace Chef server deployment scripts (moderate complexity)
3. Integrate InSpec testing with Ansible workflow (moderate complexity)
4. Set up AWX/Tower as replacement for Chef Automate features (high complexity, dependencies)

### Assumptions

1. The primary purpose of Chef in this repository is for compliance testing via InSpec, not for configuration management
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure alternatives
4. The organization wants to maintain compliance testing capabilities currently provided by InSpec
5. The repository is primarily used for demonstration/example purposes rather than production deployments
6. No external Chef cookbooks or complex Chef-specific features are being used that would require significant refactoring