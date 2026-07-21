# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring proper integration between components

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

After thorough examination using file_search for patterns "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository.

The repository contains the following components that need migration:

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any VM (on-prem or cloud)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate if still needed, or migrate completely to Ansible AWX/Tower
- **Chef Infra Server**: Replace with Ansible roles for deploying Chef Infra Server if still needed, or migrate completely to Ansible AWX/Tower
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Maintain as-is for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be preserved in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production.
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. Ensure this security check is maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to Ansible playbooks will require careful handling of the Chef Automate CLI commands and ensuring idempotence.
- **InSpec Integration**: Ensuring that Chef InSpec tests continue to work with the migrated Ansible playbooks, possibly by integrating with Ansible Tower/AWX for compliance reporting.
- **Test Kitchen Replacement**: Replacing Test Kitchen with Ansible Molecule for testing while maintaining the same level of validation.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need standardization
2. **Chef Automate/Infra Server Deployment Scripts**: Moderate complexity, convert bash scripts to Ansible playbooks
3. **Testing Framework**: Replace Test Kitchen with Ansible Molecule while preserving InSpec tests

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Infra Server deployment is still required after migration (rather than being replaced entirely by Ansible Tower/AWX).
3. Chef InSpec will continue to be used for compliance testing even after migration to Ansible.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in production.
5. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.