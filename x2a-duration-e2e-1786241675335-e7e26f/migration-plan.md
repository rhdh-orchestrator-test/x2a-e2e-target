# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec compliance testing functionality within an Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Maintain InSpec tests but integrate with Ansible using the ansible_inspec module or Molecule's verifier
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for infrastructure management and compliance reporting

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml that disables SSLv3
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates; consider using Let's Encrypt in production
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled; ensure this security check is maintained
- **Vault/secrets management**: 
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (username, password)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible requires proper integration with Molecule or custom test runners
- **Chef Server Replacement**: If Chef Server functionality is needed, determine whether to use AWX/Tower or another configuration management solution
- **Idempotency**: Ensure all converted scripts maintain idempotency (especially the Chef deployment scripts)

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Refactor into Ansible role structure with proper variables
   - Update Kitchen tests to use Molecule

2. **poodle_fix.yml** (low risk, already Ansible)
   - Refactor into Ansible role structure
   - Consider merging with website_https role as an optional security feature

3. **Chef deployment scripts** (moderate complexity)
   - Convert to Ansible playbooks
   - Replace hardcoded credentials with Ansible Vault
   - Consider using existing Ansible roles for Chef Server deployment if still needed

### Assumptions

1. The primary goal is to standardize on Ansible, not necessarily to replace Chef Server functionality
2. InSpec tests should be preserved for compliance verification
3. The current setup is for testing/demonstration purposes, not production
4. No external Chef cookbooks or complex Chef configurations need migration
5. The repository is primarily educational/example code rather than production infrastructure
6. No complex data migration is required from Chef to Ansible
7. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions