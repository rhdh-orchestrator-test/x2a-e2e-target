# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** for a single engineer to complete the migration, test, and document the new solution.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys only Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file that verifies HTTPS configuration and security

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing, but integrate with Ansible workflow

### Security Considerations

- **SSL/TLS Configuration**: The repository includes security hardening for Apache (POODLE vulnerability fix)
  - Migration approach: Preserve the same security configurations in Ansible playbooks
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Use Ansible's openssl modules as already implemented

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible
  - Mitigation: Create an Ansible role that performs the same system configurations and downloads/installs Chef Automate
  
- **InSpec Integration**: Maintaining InSpec testing within an Ansible-only workflow
  - Mitigation: Use Ansible's command module to execute InSpec tests or migrate to Molecule with Testinfra

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Refactor into proper Ansible roles structure
   - Update to use Ansible Vault for any sensitive data
   
2. **InSpec Tests** - Moderate complexity
   - Integrate InSpec tests with Ansible workflow
   - Consider migrating to Molecule for testing
   
3. **Chef Deployment Scripts** - High complexity
   - Create Ansible roles to replace Chef Automate and Chef Server deployment scripts
   - Implement idempotent deployment logic

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The Chef Automate and Chef Server deployment scripts are intended for development/lab environments
3. The hardcoded credentials in the deployment scripts are not used in production environments
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The migration will maintain the same level of security hardening present in the original code
6. The InSpec tests will continue to be used for compliance verification after migration