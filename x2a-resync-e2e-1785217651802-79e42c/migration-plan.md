# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository is relatively small and appears to be primarily for demonstration purposes rather than a full production infrastructure. The migration scope is limited, with a focus on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Server deployment scripts to Ansible

Given the limited scope and small number of files, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

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

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Will need to be converted to Ansible-compatible test.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be converted to Ansible-compatible test.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for test environments)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and compliance checks

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for version control of Ansible playbooks and roles

### Security Considerations

- **SSL Configuration**: The existing playbooks configure Apache with SSL. Ensure the migrated Ansible roles follow current best practices for SSL/TLS configuration.
  - Migration approach: Update the SSL protocols to use only TLS 1.2+ and modern cipher suites

- **SSH Hardening**: The InSpec tests check for SSH root login being disabled.
  - Migration approach: Include the `ansible-hardening` role or the `dev-sec.ssh-hardening` role from Ansible Galaxy

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require additional expertise.
  - Mitigation: Use Molecule's verifier plugins or custom Ansible tasks with assert module

- **Chef Automate Functionality**: Chef Automate provides compliance scanning and reporting that will need equivalent solutions in the Ansible ecosystem.
  - Mitigation: Consider integrating with tools like OpenSCAP, Compliance as Code, or commercial solutions like Ansible Tower with compliance plugins

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need refactoring to follow best practices and role-based structure
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, need conversion to Ansible-compatible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, need complete rewrite as Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The InSpec tests are used for compliance validation and not for continuous testing in a CI/CD pipeline
3. The deployment scripts are used for setting up test environments and not production Chef servers
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. There are no external dependencies or integrations not visible in the repository
6. The migration will maintain the same level of security compliance as the original configuration
7. The Apache configuration and SSL settings will remain functionally equivalent after migration