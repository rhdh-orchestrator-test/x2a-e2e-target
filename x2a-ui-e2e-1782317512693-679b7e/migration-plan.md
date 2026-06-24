# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a single engineer, with minimal complexity.

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
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (STIG)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be reused as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and handling

- **SSH Security**: Preserve the SSH hardening checks from ssh_profile.rb
  - Convert InSpec controls to Ansible assertions or Molecule tests
  - Maintain compliance with security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the equivalent assertions and checks
  - Mitigation: Use Molecule's verifier plugins or custom Ansible tasks for verification

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks
  - Mitigation: Create idempotent Ansible tasks that perform the same system configurations and installations

### Migration Order

1. **website_https.yml** (already Ansible, no migration needed)
2. **poodle_fix.yml** (already Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible/Molecule tests)
4. **ssh_profile.rb** (convert InSpec controls to Ansible/Molecule tests)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible playbooks)

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
3. The deployment scripts for Chef Automate and Chef Infra Server are still needed (rather than being eliminated)
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No additional security requirements beyond what's currently implemented
6. No integration with external systems beyond what's currently configured