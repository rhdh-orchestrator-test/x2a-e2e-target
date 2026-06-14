# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, focusing on:

1. Existing Ansible playbooks that need to be reviewed and potentially refactored
2. Chef InSpec tests that need to be converted to Ansible-compatible testing frameworks
3. Bash scripts for Chef infrastructure deployment that need to be converted to Ansible playbooks

Given the limited scope and relatively simple configurations, this migration is estimated to be **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS** for a single engineer.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Chef InSpec verification
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Use ansible-lint for static analysis and custom Ansible playbooks for verification
  - Option 3: Maintain InSpec as a standalone testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or adapt existing kitchen.yml to work with Ansible-only testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for centralized automation
  - Ansible Collections for compliance scanning functionality

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security by enforcing TLSv1.2. This security hardening should be maintained in the migrated solution.
  
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This security check should be maintained in the migrated solution.

- **Vault/secrets management**:
  - Hardcoded credentials in Bash scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates in the website_https.yml playbook should use Ansible Vault for private key storage

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-compatible testing frameworks will require mapping InSpec resources to equivalent Ansible/testinfra assertions.
  - Mitigation: Create a mapping document for InSpec to testinfra/Ansible assertions and validate each test case individually.

- **Chef Server Deployment**: The Chef server deployment scripts contain specific Chef commands that need Ansible equivalents.
  - Mitigation: Research Ansible modules for package installation and use command/shell modules with idempotency checks for Chef-specific commands.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need refactoring for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity to convert to Ansible testing framework
3. **Bash Scripts** (deploy-automate.sh, deploy-chef-server.sh): Highest complexity as they need complete rewriting as Ansible playbooks

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 as specified in the kitchen.yml file.
2. The migration will maintain the same functionality but doesn't require maintaining Chef Automate/Infra Server (these will be replaced with Ansible equivalents).
3. The InSpec tests are currently used for compliance verification and this functionality needs to be preserved in the Ansible migration.
4. The hardcoded credentials in the Bash scripts are for demonstration purposes and will be replaced with secure credential management in the Ansible implementation.
5. The self-signed certificates in the website_https.yml playbook are acceptable for the use case and don't need to be replaced with CA-signed certificates.
6. The Test Kitchen integration is used for development/testing only and can be replaced with an equivalent Ansible testing framework.