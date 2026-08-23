# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more standardized Ansible structure and migrating the Chef InSpec tests to Ansible's native testing capabilities. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module
  - For more complex compliance testing: Use ansible-lint or Molecule for testing
  - Alternative: Convert InSpec tests to use with ansible-test

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure setup
  - AWX/Ansible Tower for enterprise automation platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security:
  - Ensure TLS 1.2+ is enforced (as in the current poodle_fix.yml)
  - Consider adding more modern security headers
  - Use Ansible Vault for storing sensitive information

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Maintain SSH hardening checks in the Ansible equivalent
  - Consider using ansible-lockdown or similar security roles

- **Vault/secrets management**:
  - Current scripts contain hardcoded credentials in the Chef deployment scripts
  - Migration should use Ansible Vault to secure these credentials
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests:
  - Challenge: InSpec has specific testing syntax for SSL/TLS checks
  - Mitigation: Use Ansible's uri module with appropriate SSL parameters or custom modules

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Challenge: The scripts use Chef-specific CLI tools
  - Mitigation: Research if Chef provides API access or alternative deployment methods that can be used with Ansible modules

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to Ansible role structure
2. **poodle_fix.yml** (low risk, already Ansible): Convert to Ansible role structure
3. **InSpec Tests** (moderate complexity): Convert to Ansible assertions or Molecule tests
4. **Chef Deployment Scripts** (high complexity): Create Ansible playbooks for Chef infrastructure deployment

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The migration aims to standardize on Ansible and remove Chef dependencies where possible
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The deployment scripts are used for setting up test/development environments and not production systems (given the hardcoded credentials)
5. The current Test Kitchen setup is primarily for testing and can be replaced with Ansible-native testing tools