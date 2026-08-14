# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used together to deploy and validate secure web applications. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes scripts for setting up Chef Automate and Chef Infra Server environments.

The migration scope is relatively small, as the repository already contains Ansible playbooks. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (STIG)

- **automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. Migration consideration: Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use Ansible assert module and register variables
  - For comprehensive testing: Implement Ansible Molecule with testinfra or Goss
  - For compliance testing: Consider OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL hardening as a separate task file.

- **SSH Hardening**: The InSpec tests validate SSH security configurations.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same security controls tested by the InSpec profile.

- **Self-signed Certificates**: The playbook generates self-signed certificates.
  - Migration approach: Use the same Ansible openssl_* modules but consider adding options for using proper CA-signed certificates in production.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation strategy: Use Ansible assert module for simple tests, and Molecule with testinfra for more complex validation.

- **Chef Automate Replacement**: Determining if Chef Automate functionality needs to be replaced.
  - Mitigation strategy: Evaluate if AWX/Ansible Tower can provide similar functionality or if a different compliance tool is needed.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Refactor into a proper Ansible role structure
2. **poodle_fix.yml** (low risk, already Ansible): Integrate into the Apache role as a security task
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing solutions
4. **Chef Automate/Server Scripts** (high complexity): Replace with Ansible AWX/Tower deployment if needed

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing.
2. The existing Ansible playbooks are functional and follow best practices.
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Infra Server.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The migration will include improving the structure of existing Ansible content to follow best practices (roles, collections).
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure alternatives.