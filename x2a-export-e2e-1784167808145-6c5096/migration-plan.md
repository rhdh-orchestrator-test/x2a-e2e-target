# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks demonstrating compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: Preserve the SSH security checks from the InSpec profile
  - Ensure root login remains disabled
  - Maintain compliance with security standards referenced in the InSpec test

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's expectations
  - Consider using community.general.test module for more test-oriented assertions

- **SSL Testing**: Replicating InSpec's SSL protocol testing capabilities in Ansible
  - Mitigation: Create custom Ansible modules or use shell commands with assert to verify SSL configurations

- **Deployment Script Conversion**: Converting the Chef deployment bash scripts to idempotent Ansible playbooks
  - Mitigation: Break down the scripts into discrete tasks and use Ansible's package management and command modules

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already in Ansible format, no migration needed)
2. **website_https_verify.rb** (convert InSpec test to Ansible assertions)
3. **ssh_profile.rb** (convert InSpec SSH security checks to Ansible)
4. **deploy-chef-server.sh** and **deploy-automate.sh** (convert to Ansible playbooks)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification beyond potential best practice improvements.
2. The InSpec tests are currently being used for validation and their functionality needs to be preserved in the Ansible migration.
3. The deployment scripts are used for setting up Chef infrastructure that may be replaced by Ansible Tower/AWX or other Ansible-based solutions.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security requirements specified in the InSpec tests (particularly the SSH profile) need to be maintained in the migrated solution.
6. Test Kitchen is currently used for development and testing, and a replacement or continued use strategy is needed.
7. No external data sources or integrations beyond what's visible in the repository are required for the functionality.