# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Files: website_https.yml
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Files: poodle_fix.yml
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website and SSH configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Files: website_https_verify.rb, ssh_profile.rb
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification, SSH security compliance

- **chef-deployment-scripts**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Files: deploy-automate.sh, deploy-chef-server.sh
    - Key Features: Chef Automate and Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the Chef and Ansible integration
- `README.md`: Main repository documentation

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Red Hat Ansible Automation Platform for enterprise automation
  - GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with SSL. Ensure the migrated playbooks:
  - Use modern TLS protocols (TLS 1.2+)
  - Implement proper cipher suites
  - Generate appropriate key lengths

- **SSH Hardening**: The InSpec profile checks for SSH root login. Ensure the migrated solution:
  - Implements equivalent SSH hardening
  - Maintains compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault or an external secrets manager

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing will require:
  - Understanding the current test coverage
  - Implementing equivalent tests in the new framework
  - Ensuring all compliance checks are maintained

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting:
  - Identify an equivalent solution in the Ansible ecosystem
  - Ensure data migration from Chef Automate to the new solution

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible format)
2. **poodle-vulnerability-fix** (low risk, already in Ansible format)
3. **inspec-tests** (moderate complexity, requires framework change)
4. **chef-deployment-scripts** (high complexity, requires complete rewrite)

### Assumptions

1. The current setup uses Chef primarily for testing (InSpec) while actual configuration is done with Ansible
2. The deployment scripts are used for setting up Chef infrastructure, not for configuring applications
3. There are no additional Chef cookbooks or recipes not visible in the provided directory structure
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The migration will maintain the same level of security compliance currently implemented
6. No custom Chef resources or libraries are in use that would require special handling
7. The Test Kitchen setup is primarily used for testing Ansible playbooks, not Chef cookbooks