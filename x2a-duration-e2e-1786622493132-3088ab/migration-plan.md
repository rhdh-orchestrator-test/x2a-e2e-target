# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

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

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration (root login disabled)

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible role for Chef Automate deployment or consider migrating to alternative solutions like AWX/Ansible Tower
- **Chef InSpec**: Maintain as-is for compliance testing, as it works well with Ansible
- **Test Kitchen with Ansible**: Consider migrating to Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols. This should be maintained in the migrated solution.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. This security check should be preserved.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **Vault/secrets management**: 
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require careful testing to ensure all components are properly installed and configured.
  - Mitigation: Create a dedicated Ansible role for Chef Automate deployment with appropriate variables and templates.

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible playbooks.
  - Mitigation: Maintain the existing InSpec tests and update the Ansible playbook structure to match the expected outputs.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Simply reorganize into proper Ansible roles structure.
2. **Chef Deployment Scripts**: Convert to Ansible roles with appropriate variables and templates.
3. **Testing Framework**: Update testing framework to use Molecule while maintaining InSpec tests.

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be run on a fresh Ubuntu 20.04 system.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced in a production environment.
4. The InSpec tests are meant to be run against the systems configured by the Ansible playbooks to verify compliance.
5. The migration goal is to maintain the same functionality but using Ansible exclusively, rather than a mix of technologies.
6. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already well-structured and may only need reorganization into roles.