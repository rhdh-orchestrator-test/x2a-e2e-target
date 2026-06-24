# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests used for compliance verification
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary migration effort will involve replacing Chef InSpec tests with Ansible-native solutions and converting Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or Molecule for testing
  - For advanced compliance: Consider integrating with OpenSCAP or using ansible-compliance collection

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-native management platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Maintain the same SSL configuration in Ansible playbooks, but update to modern best practices.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1: InSpec Test Conversion**
  - Description: Converting InSpec tests to Ansible-native verification
  - Mitigation strategy: Use Ansible assert module for simple checks, and consider ansible-test or Molecule for more complex verification

- **Challenge 2: Chef Server Deployment**
  - Description: Replacing Chef Server deployment with Ansible management solution
  - Mitigation strategy: Evaluate AWX/Tower as a replacement for Chef Automate/Server or consider other Ansible-native management platforms

### Migration Order

1. **website_https_verify and ssh_profile** (InSpec tests): Convert to Ansible assertions or Molecule tests
2. **chef-automate-deployment and chef-server-deployment**: Convert to Ansible playbooks for infrastructure setup
3. **kitchen.yml**: Replace with Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The migration will maintain the same functionality but using Ansible-native solutions.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The InSpec tests are used for verification only and not for remediation.
7. The deployment scripts are intended for demonstration/lab environments, not production.