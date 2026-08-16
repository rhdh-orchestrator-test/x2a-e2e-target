# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure and integrating Chef InSpec tests into an Ansible-based compliance workflow. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks and moderate complexity for integrating the compliance testing framework.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG references

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Static HTML content for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate InSpec with Ansible using the inspec_exec module from community.general collection

- **Test Kitchen**: Replace with:
  - molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the Apache SSL configuration to an Ansible template with appropriate security settings

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that applies the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely using ansible-vault for private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting Chef InSpec tests to equivalent Ansible verification
  - Mitigation: Use the ansible.builtin.assert module for simple tests and community.general.inspec_exec for complex compliance tests

- **Compliance Reporting**: Maintaining compliance reporting capabilities when moving from InSpec
  - Mitigation: Integrate with tools like Ansible Tower/AWX for compliance reporting or use community.general.inspec_exec to continue using InSpec for testing

- **Certificate Management**: Ensuring secure certificate generation and management
  - Mitigation: Use the ansible.builtin.openssl_* modules with proper vault integration for secure key storage

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration playbook, low risk, high value
2. **poodle_fix.yml** (Priority 1): Security hardening playbook, low complexity
3. **InSpec Tests** (Priority 2): Convert or integrate compliance testing framework
4. **Deployment Scripts** (Priority 3): Convert Chef Automate/Infra Server deployment scripts to Ansible roles

### Assumptions

1. The current Ansible playbooks are functional and tested in the existing environment
2. The InSpec tests are used for compliance validation and not for active remediation
3. There is no existing Ansible inventory or group_vars structure in the repository
4. The deployment scripts are used for initial setup and not for ongoing configuration management
5. There are no external dependencies or integrations not visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The migration will standardize on Ansible 2.9+ features and modules
8. No custom Ansible modules or plugins will be required for the migration