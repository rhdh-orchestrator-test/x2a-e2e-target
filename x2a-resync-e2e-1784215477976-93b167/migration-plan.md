# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic assertions
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing and verification

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are preserved during migration
  - Maintain the TLSv1.2 requirement and SSLv3 disablement

- **SSH Security**: The SSH root login check must be preserved in the new testing framework
  - Convert the InSpec control to an equivalent Ansible assertion or Molecule test

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the detailed InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use a combination of Molecule and custom Ansible assertions to replicate InSpec functionality
  - Consider using the ansible.posix collection for more advanced system checks

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create an Ansible role that installs and configures Chef Automate using the official installation methods
  - Use Ansible's uri module to interact with Chef Automate API for configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update to current Ansible best practices
   - Convert to roles for better organization

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Molecule tests or Ansible assertions
   - Ensure all security checks are preserved

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The existing Ansible playbooks are compatible with current Ansible versions and don't require significant updates
2. The InSpec tests are used primarily for validation and can be replaced with equivalent Ansible testing mechanisms
3. The deployment scripts are used for initial setup and not for ongoing management of Chef infrastructure
4. There is no requirement to maintain backward compatibility with Chef InSpec after migration
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The security requirements specified in the InSpec tests (especially SSH hardening) must be maintained
7. The self-signed certificates approach is acceptable for the migrated solution