# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks, primarily focused on demonstrating how Chef InSpec can be used for compliance testing alongside Ansible deployments. The migration scope is relatively small, with a focus on:

1. Preserving the compliance testing capabilities currently provided by Chef InSpec
2. Maintaining the existing Ansible playbook functionality
3. Migrating Chef server/Automate deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server deployment. No migration needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for infrastructure testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login restriction must be preserved in the migrated solution
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated during deployment
  - Total credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with an Ansible-native solution while maintaining the same level of compliance testing capability
  - Mitigation: Evaluate Ansible Molecule with Testinfra or Goss as alternatives, or consider keeping InSpec as a standalone tool
  
- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Ansible Molecule which provides similar functionality in an Ansible-native way

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, only need minor adjustments to work with new testing framework
2. **Chef InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible-native testing solution
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The Chef Automate and Chef Server deployment scripts are intended for demonstration purposes
3. There are no external dependencies or modules not visible in the repository structure
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The migration will maintain the same level of security compliance testing
6. No actual Chef cookbooks or recipes need migration as none were found in the repository