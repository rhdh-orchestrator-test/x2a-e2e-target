# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for Chef server deployment. The migration scope is relatively small, focusing on standardizing all automation to Ansible. The primary components are:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for compliance verification
3. Bash scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer. The repository appears to be primarily educational/demonstration content rather than production infrastructure code, which reduces migration risk.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, generates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates SSL vulnerabilities (POODLE) by updating Apache SSL configuration
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
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website functionality and security
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Keep InSpec tests but integrate with Ansible using the ansible_inspec module
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Apache 2.4.41**: Continue using Ansible's apache2_module and service modules

- **OpenSSL**: Continue using Ansible's openssl_* modules as already implemented

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Migration approach: Use Ansible's template module with appropriate SSL configuration

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Add Ansible tasks to configure SSH properly and verify with assert tasks

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules as already implemented, consider adding option for Let's Encrypt integration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Chef InSpec Tests**: Converting InSpec tests to Ansible-native verification
  - Mitigation: Use Ansible assert modules or maintain InSpec as a testing tool called from Ansible

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment with proper idempotence checks

### Migration Order

1. **website-https-configuration** (already in Ansible, no migration needed)
2. **poodle-ssl-fix** (already in Ansible, no migration needed)
3. **InSpec Tests** (convert to Ansible assert tasks or Molecule tests)
4. **Chef Server Deployment Scripts** (convert to Ansible roles)

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production infrastructure
2. The Chef InSpec tests are used for verification only and not for active remediation
3. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with secure values in production
4. The self-signed certificates are acceptable for the demonstration environment
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file