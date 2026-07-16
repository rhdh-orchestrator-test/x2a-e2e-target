# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration
  - GitLab CI/Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The current implementation fixes POODLE vulnerability by enforcing TLSv1.2. This should be maintained in the Ansible migration.
  - Migration approach: Use the same `replace` module approach or consider using the `lineinfile` module for more precise control.

- **SSH Security**: The InSpec test verifies SSH root login is disabled.
  - Migration approach: Create an equivalent Ansible task using the `assert` module or integrate with ansible-lint rules.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly; consider using Ansible Vault for storing pre-generated certificates in production environments

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require understanding the equivalent testing patterns.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and assertions.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced with Ansible equivalents.
  - Mitigation: Clearly document which Chef Automate features are being used and identify Ansible alternatives for each.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks
   - Convert to roles for better organization

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or compliance checks

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is demonstration, not production use
2. The InSpec tests are used for validation after Ansible playbook execution
3. The deployment scripts are used for setting up test environments
4. No external Chef cookbooks or complex Chef resources are being used
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No complex state management or data bags are being used
7. The security requirements (TLSv1.2, SSH configuration) need to be maintained in the migration
8. The deployment scripts contain hardcoded credentials that would need to be secured in a production environment