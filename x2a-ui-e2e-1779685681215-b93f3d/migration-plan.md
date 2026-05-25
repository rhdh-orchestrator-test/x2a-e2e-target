# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring existing Ansible playbooks follow best practices
3. Replacing Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains examples rather than production infrastructure code

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file, likely used as a template or example. Can be directly incorporated into Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-lint for static code analysis

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and API
  - Ansible Semaphore for lightweight UI
  - GitLab CI/CD or GitHub Actions for automation pipelines

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3. This security hardening should be maintained in the migrated Ansible roles.
  - Migration approach: Create dedicated Ansible role for Apache SSL hardening

- **SSH Security**: The InSpec tests verify SSH root login is disabled, which is a critical security control.
  - Migration approach: Create Ansible role that enforces SSH security settings and includes verification tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using ansible-vault for storing private keys
  - Document the count and type of credentials detected per module:
    - chef-automate-deploy: 1 password in plaintext
    - chef-server-deploy: 1 password in plaintext

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests requires understanding the testing semantics of both frameworks.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible automation requires understanding of AWX/Tower or alternative deployment.
  - Mitigation: Create Ansible roles for deploying AWX/Tower or alternative solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible-compatible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires replacement with Ansible roles for alternative solutions

### Assumptions

1. The repository appears to be primarily for demonstration/example purposes rather than production infrastructure
2. The InSpec tests are used for validating the Ansible playbooks, suggesting a hybrid approach to infrastructure as code
3. The deployment scripts contain hardcoded credentials that would need to be secured in a production environment
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The Apache configuration is basic and focused on HTTPS setup rather than complex web application hosting
6. There are no complex data transformations or Chef-specific resources that would be difficult to migrate
7. The repository does not contain Chef cookbooks, only InSpec tests and Ansible playbooks
8. The migration is primarily focused on standardizing on Ansible rather than addressing functional gaps