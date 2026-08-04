# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining the InSpec testing framework for compliance validation

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** due to the limited number of components and straightforward configurations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Chef Server CLI**: Replace with Ansible roles for configuration management server deployment
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing approach
- **InSpec**: Maintain as compliance testing framework, integrate with Ansible workflow

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be preserved in the migrated solution.
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This compliance check should be maintained.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef Automate/Server Deployment**: Converting the Chef deployment scripts to Ansible requires understanding of Chef Automate architecture. Consider using the official Chef Automate Ansible role if available, or creating a custom role.
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible workflow. This can be addressed by maintaining the existing test files and updating the execution method.
- **Test Kitchen**: Updating the Test Kitchen configuration to work with the new Ansible structure while maintaining the same testing capabilities.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need standardization
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, requires converting bash scripts to Ansible roles
3. **Testing Framework** (kitchen.yml, InSpec tests): Medium complexity, requires integration with new Ansible structure

### Assumptions

1. The primary goal is to standardize on Ansible as the sole configuration management tool
2. Chef InSpec will continue to be used for compliance testing
3. The Chef Automate and Chef Infra Server instances being deployed are for managing other systems, not for direct use in this repository
4. The hardcoded credentials in the deployment scripts are for testing purposes only
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. Vagrant will continue to be used for local testing
7. No external dependencies or third-party modules are required beyond what's explicitly referenced in the repository