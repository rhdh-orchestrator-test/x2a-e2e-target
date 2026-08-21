# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the Chef InSpec tests for compliance verification

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as-is for compliance testing or migrate to Ansible's built-in testing capabilities
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-based configuration management solution

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates that should be preserved in the migration
- **SSH Hardening**: The SSH security profile tests must continue to pass after migration
- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef InSpec Integration**: Ensuring that the existing InSpec tests continue to work with the migrated Ansible playbooks
- **Chef Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate functionality
- **Test Kitchen to Molecule Migration**: Converting the existing test framework to Ansible Molecule

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they are already in Ansible format, just need review and potential refactoring
2. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity as they need to be converted from Bash/Chef to Ansible playbooks

### Assumptions

1. The InSpec tests are to be preserved as-is and not converted to Ansible-native testing
2. The Chef Automate and Chef Infra Server functionality needs to be replaced with equivalent Ansible tooling
3. The target environment will continue to be Ubuntu 20.04 or compatible
4. The repository is primarily for demonstration/example purposes rather than production use
5. The hardcoded credentials in the deployment scripts are for demonstration only and will be properly secured in the migration