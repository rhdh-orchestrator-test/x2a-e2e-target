# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are properly implemented in the Ansible ecosystem

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

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
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the SSL protocol restrictions are preserved in the migrated Ansible roles
  
- **SSH Security**: The SSH root login compliance check must be preserved
  - Approach: Convert the InSpec control to an Ansible task that checks and enforces the same policy

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
    - Migration approach: Replace with Ansible Vault for secure credential storage
  - Self-signed certificates in website_https.yml
    - Migration approach: Maintain the same OpenSSL functionality but consider integration with Ansible Vault for key storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Research and implement appropriate Ansible testing frameworks (Molecule, assert module, etc.)
  
- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform the same installation and configuration steps

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires complete rewrite as Ansible playbooks)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The self-signed certificates approach is acceptable for the migrated solution
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The Chef Automate and Chef Infra Server deployment scripts are intended to be migrated to Ansible, not preserved as-is
7. The repository is primarily for demonstration purposes as indicated by the main README.md