# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-native testing solutions
2. Preserving the existing Ansible playbooks with minimal changes
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that most of the infrastructure code is already in Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for integration testing
  - Use Ansible's `assert` module for in-playbook validation
  - Consider Molecule for more comprehensive testing
  - Alternative: Integrate with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Simple Vagrant or Docker-based testing workflows managed by Ansible

- **Chef Automate/Server**: Replace with:
  - Ansible AWX or Ansible Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain the restriction to TLSv1.2 protocol
  - Consider updating to also allow TLSv1.3 for modern security

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
  - Create an Ansible task to validate and enforce SSH root login restrictions
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks
  - Mitigation: Use Ansible's assert module with appropriate conditionals to check the same conditions
  - For complex tests, consider using the ansible.builtin.shell module to run commands and validate output

- **Compliance Validation**: Ensuring the same level of compliance checking without InSpec
  - Mitigation: Consider using OpenSCAP with Ansible for compliance scanning or maintaining a separate compliance validation tool

- **User Management**: Replacing Chef Server's user and organization management
  - Mitigation: Implement Ansible roles for user management with appropriate RBAC

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Chef Automate/Server Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible roles for infrastructure management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. No external Chef cookbooks or complex Chef-specific features are being used
5. The security compliance requirements (STIG references in ssh_profile.rb) will remain relevant in the migrated solution
6. The self-signed certificates are for testing only and not production use
7. The hardcoded credentials in the setup scripts are for demonstration purposes only