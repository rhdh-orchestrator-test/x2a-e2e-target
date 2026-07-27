# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that are already in place
3. Maintaining the Chef InSpec testing capabilities within the Ansible workflow

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks, as most of the infrastructure is already using Ansible playbooks with Chef InSpec for testing.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as a testing tool within Ansible workflow
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain with Ansible provisioner
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **POODLE Vulnerability Mitigation**: The poodle_fix.yml playbook specifically addresses SSL security. This should be preserved in the migration.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificate generation and management
  - Recommendation: Use Ansible Vault to secure credentials

### Technical Challenges

- **Chef InSpec Integration**: Ensuring Chef InSpec tests continue to work with pure Ansible deployment
  - Mitigation: Use Ansible's built-in integration with InSpec or migrate to Ansible's native testing capabilities
  
- **Chef Automate/Server Deployment**: Converting bash scripts to idempotent Ansible playbooks
  - Mitigation: Use Ansible's package management modules and command modules with appropriate conditionals

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** (high value, moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credentials

2. **Test Kitchen Configuration** (low risk)
   - Migrate to Ansible Molecule or update Test Kitchen configuration

3. **Existing Ansible Playbooks** (low risk)
   - Review and optimize existing playbooks
   - Ensure they follow Ansible best practices

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "examples" and "companion to a white paper".

2. The Chef InSpec tests are intended to be maintained as part of the compliance automation strategy, even after migrating to pure Ansible.

3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments rather than production infrastructure.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.

5. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already following Ansible best practices and may not need significant changes.