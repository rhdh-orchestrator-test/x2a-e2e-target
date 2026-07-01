# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The migration will primarily involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for Apache

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules for basic compliance checks
  - Option 3: Integrate with OpenSCAP for more comprehensive compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the SSL protocol restrictions are preserved in the migrated Ansible tasks

- **SSH Security**: The SSH root login restrictions tested by ssh_profile.rb must be enforced
  - Approach: Create an Ansible task to configure SSH properly and add appropriate tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with tools like testinfra for more complex tests

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible/Molecule tests)
4. **ssh_profile.rb** (convert InSpec tests to Ansible/Molecule tests)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible playbooks or replace functionality)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be needed in an Ansible-only environment.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The migration will focus on preserving the functionality and security aspects of the original code.
6. The organization may want to replace Chef Automate/Infra Server with Ansible AWX/Tower for similar functionality.