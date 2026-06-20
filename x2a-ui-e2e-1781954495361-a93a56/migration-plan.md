# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for verifying compliance

The migration complexity is low to medium, as most of the configuration is already in Ansible format. The estimated timeline for migration is 1-2 weeks, primarily focusing on converting the InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. No migration considerations needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for simpler testing
  - Option 3: Use the ansible.builtin.assert module for basic compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Consider migrating to:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins with Ansible for CI/CD pipeline integration

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration maintains:
  - Proper SSL certificate generation and management
  - Secure protocol settings (TLSv1.2 only, as in poodle_fix.yml)
  
- **SSH Security**: The ssh_profile.rb InSpec test checks for secure SSH configuration:
  - Ensure the migration includes equivalent checks for SSH root login being disabled
  - Consider expanding SSH hardening in the Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions:
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents
  - Mitigation: Use Molecule with Testinfra or Goss, which provide similar testing capabilities

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts:
  - Challenge: Chef Automate provides specific compliance and reporting features
  - Mitigation: Evaluate Ansible Automation Platform or AWX as replacements, or consider keeping Chef Automate for compliance while using Ansible for configuration management

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbooks
   - Consider converting to Ansible roles for better organization

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible Molecule tests
   - Convert ssh_profile.rb to Ansible Molecule tests
   - Implement equivalent compliance checks using Ansible-native tools

3. **Chef Automate Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts for deploying automation platform
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary goal is to migrate all components to Ansible, including testing capabilities currently provided by Chef InSpec.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. Vagrant will continue to be used for development/testing environments.
4. The security compliance requirements (SSH configuration, SSL protocols) will remain the same.
5. The repository is primarily for demonstration purposes, as indicated by the README.md mentioning it's a companion to a white paper.
6. No external data sources or complex state management is required beyond what's visible in the repository.
7. The migration will need to maintain the same level of compliance automation currently achieved with the Chef InSpec and Ansible combination.