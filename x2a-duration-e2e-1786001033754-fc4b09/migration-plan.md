# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure a web server with HTTPS
2. Chef InSpec tests for compliance verification
3. Bash scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main work involves converting the Chef InSpec tests to Ansible-compatible testing frameworks and refactoring the Chef Automate deployment scripts into Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website-https-compliance**:
    - Description: Chef InSpec test that verifies HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh-compliance**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec as a standalone tool that can be called from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Collections for configuration management
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the Ansible migration.
  - Migration approach: Use the `openssl_*` modules in Ansible as already implemented

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for basic tests, or integrate with Molecule for more comprehensive testing.

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible Tower/AWX setup.
  - Mitigation: Create Ansible playbooks to install and configure AWX/Tower, with roles for user and organization management.

### Migration Order

1. **website-https** and **poodle-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks
   - Convert to Ansible roles for better organization

2. **InSpec Tests** (moderate complexity)
   - Convert InSpec tests to Ansible assert statements or Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation.
2. The Chef deployment scripts are used for setting up a test environment and are not part of the main application.
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
4. The migration will maintain the same level of security compliance as the original implementation.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives in the migration.