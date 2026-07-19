# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec tests continue to work with the new Ansible-only approach. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible/InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations: Already in Ansible format, may need refactoring to follow best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability. Migration considerations: Already in Ansible format, may need refactoring.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Update to use Ansible-only approach.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Migration considerations: Keep as is, as InSpec can work with Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Migration considerations: Keep as is, as InSpec can work with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Replace with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook or remove if Chef server is no longer needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based solution
- **InSpec**: Keep as is for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the secure TLS 1.2 configuration and disable insecure protocols (SSL3)
- **SSH Security**: Maintain SSH hardening as verified by the InSpec tests
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is acceptable but could be improved with proper certificate management

### Technical Challenges

- **Chef Server Replacement**: Determining if Chef Server functionality needs to be replaced with an Ansible equivalent (AWX/Tower) or if it can be eliminated entirely
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible-only approach
- **Configuration Management**: Ensuring all configuration managed by Chef is properly migrated to Ansible

### Migration Order

1. **chef-and-ansible playbooks** (low risk, high value): Already in Ansible format, just need refactoring
2. **InSpec tests** (low risk, high value): Keep as is, ensure they work with the new Ansible approach
3. **Chef deployment scripts** (moderate complexity): Replace with Ansible playbooks for deploying configuration management infrastructure

### Assumptions

1. The Chef Automate and Chef Infra Server deployment is for managing infrastructure that will now be managed by Ansible instead
2. InSpec will continue to be used for compliance testing with Ansible
3. The target environment will remain Ubuntu 20.04 or similar
4. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives
5. The repository is primarily for demonstration purposes (as indicated in the README) rather than production use