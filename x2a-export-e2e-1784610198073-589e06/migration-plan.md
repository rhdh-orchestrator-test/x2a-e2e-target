# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration, along with bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **2-3 weeks** for a small team (1-2 engineers). The repository primarily contains examples and demonstrations rather than production infrastructure code, which simplifies the migration process.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and bash scripts that need individual migration planning:

### MODULE INVENTORY

**Note: After thorough searching, no traditional modules with manifests/init.pp (Puppet), recipes/default.rb (Chef), or .psd1 manifests (PowerShell) were found in this repository.**

The following components were identified:

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the website example. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab CI/GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding modern cipher suite configurations
  - Add automatic certificate renewal if moving to Let's Encrypt

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Create equivalent Ansible tasks to enforce SSH hardening
  - Implement idempotent checks for SSH configuration

- **Credentials Management**: 
  - Current scripts contain hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh
  - Migrate to Ansible Vault for secure credential storage
  - Remove hardcoded passwords from scripts (2 instances detected)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the compliance requirements in the InSpec tests
  - Creating equivalent Ansible assertions or custom modules
  - Ensuring the same level of reporting and documentation

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible alternatives:
  - Determining which Chef Server features are actually being used
  - Mapping Chef Server functionality to Ansible Tower/AWX
  - Migrating any existing Chef cookbooks to Ansible roles (not present in this repository)

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need review and potential refactoring to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires replacing Chef-specific functionality with Ansible equivalents

### Assumptions

1. The repository is primarily for demonstration/example purposes rather than production infrastructure
2. No external Chef cookbooks or complex Chef-managed infrastructure exists beyond what's visible in the repository
3. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
4. Security compliance testing is a key requirement that must be maintained in the migration
5. The deployment scripts are used for setting up test/demo environments rather than production Chef infrastructure
6. No custom Chef resources or complex Chef-specific functionality is being used
7. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
8. The migration will maintain or improve the current security posture
9. No external integrations or APIs are being used that would complicate the migration