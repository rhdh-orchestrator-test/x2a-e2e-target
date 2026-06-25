# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with a focus on:

1. Migrating Chef InSpec tests to Ansible-compatible compliance testing solutions
2. Consolidating the existing Ansible playbooks into a more structured Ansible project
3. Replacing Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (security compliance check)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Integrate with other compliance tools like OSCAP or Lynis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Semaphore for a lightweight alternative

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Preserve the same Apache configuration in the Ansible playbooks

- **SSH Security**: The compliance checks for SSH root login must be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or integrate with ansible-lint

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
    - Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible's assert module or consider integrating with tools like Goss or Serverspec

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with compliance tools that can produce similar reports or use AWX/Tower's reporting capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need restructuring
2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, convert Bash scripts to Ansible playbooks
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Higher complexity, requires finding Ansible-compatible testing solutions

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use
2. The InSpec tests are used for validation after Ansible playbook execution
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. The repository doesn't contain actual secrets or sensitive information
8. The migration doesn't need to preserve Test Kitchen functionality as it will be replaced by Ansible-native testing tools