# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to medium complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Static HTML file, can be directly included in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Migrate to Ansible-native testing frameworks:
  - For infrastructure testing: Replace with Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider using ansible-lint with custom rules or OpenSCAP with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated Ansible roles.
- **Self-signed Certificates**: The current implementation generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Hardening**: The InSpec tests verify SSH security configurations. Ensure these checks are implemented in the Ansible roles.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require mapping InSpec resources to equivalent Testinfra or Goss checks.
  - Mitigation: Create a mapping document for InSpec resources to Testinfra/Goss equivalents
- **Chef Automate/Server Deployment**: The bash scripts for Chef deployment need to be converted to Ansible roles.
  - Mitigation: Create dedicated Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to Ansible role structure with proper variables
2. **poodle_fix.yml** (low risk, already Ansible): Convert to Ansible role structure, potentially merge with website_https role
3. **InSpec Tests** (moderate complexity): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (high complexity): Convert to Ansible roles or replace functionality

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef InSpec tests are used for compliance validation of infrastructure configured by Ansible, not for testing Chef-managed infrastructure.
3. The deployment scripts for Chef Automate and Chef Server may not need migration if the goal is to fully transition to Ansible.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in production.
5. The Test Kitchen configuration is used for local testing and development, not for CI/CD pipelines.