# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily focused on examples rather than production infrastructure code. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the website
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used for testing the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain:
  - Self-signed certificate generation
  - TLSv1.2 enforcement (disabling older protocols)
  - Proper file permissions for certificates (mode 0640)

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled in migrated configurations
  - Maintain compliance with security standards referenced in the tests (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend using Ansible Vault for storing these credentials securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible modules
  - Ensuring the same level of reporting and documentation

- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Server deployment will need to be:
  - Converted to Ansible roles or playbooks
  - Updated to use Ansible's idempotent approach rather than direct commands
  - Enhanced with proper error handling and state verification

### Migration Order

1. **website_https.yml** (already Ansible, low risk, just needs review and potential refactoring)
2. **poodle_fix.yml** (already Ansible, low risk, just needs review and potential refactoring)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (higher complexity, requires complete rewrite as Ansible roles)

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for local testing
4. The security requirements and compliance standards referenced in the InSpec tests must be maintained
5. The Chef Automate and Chef Server deployment scripts are intended to be replaced with equivalent Ansible functionality
6. No external dependencies or integrations beyond what's visible in the repository
7. The migration will maintain the same level of security hardening and compliance testing
8. Test Kitchen can be replaced with Molecule or another Ansible-native testing framework