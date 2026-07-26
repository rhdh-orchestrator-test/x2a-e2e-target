# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks used for compliance automation and infrastructure deployment. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of low complexity and can be completed within 1-2 weeks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol testing

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline automation

### Security Considerations

- **SSL Configuration**: The existing playbooks configure SSL for Apache. Migration should maintain:
  - Self-signed certificate generation
  - TLS 1.2 protocol enforcement
  - Disabling of vulnerable protocols (SSL3)

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled. Migration should:
  - Convert the InSpec test to Ansible assert or Molecule verification
  - Consider adding an Ansible task to enforce this configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic
  - Mitigation: Use Ansible's assert module with appropriate conditionals

- **Chef Server Functionality**: Replacing Chef Server's functionality with Ansible equivalents
  - Mitigation: Use AWX/Tower for web UI and API, GitLab/Jenkins for CI/CD pipelines

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible assertions or Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The repository is primarily for demonstration purposes, as indicated by the README.md
2. No production systems are directly dependent on these specific scripts
3. The InSpec tests are used for validation only and not part of a larger compliance framework
4. The hardcoded credentials in the setup scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There are no external dependencies or integrations not visible in the repository
7. The migration is focused on technology conversion rather than architectural changes