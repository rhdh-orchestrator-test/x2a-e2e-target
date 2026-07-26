# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Integrating Chef InSpec tests with Ansible or migrating to Ansible-native testing solutions

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

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
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Either:
  - Option 1: Keep InSpec as a testing tool and call it from Ansible
  - Option 2: Migrate to Ansible-native testing solutions like Molecule or ansible-test

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates that should be preserved or improved in the migration
- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be moved to Ansible Vault or another secure secret management solution

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires understanding of Chef Automate's architecture and configuration
  - Mitigation: Create an Ansible role that performs the same steps as the bash script, using Ansible modules for package installation and configuration

- **InSpec Integration**: Determining whether to keep InSpec tests or migrate to Ansible-native testing
  - Mitigation: If keeping InSpec, ensure proper integration with Ansible; if migrating, create equivalent tests using Ansible's testing frameworks

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need organization into proper roles and playbooks
2. **Chef InSpec Tests**: Moderate complexity, decide whether to keep or migrate to Ansible-native testing
3. **Chef Deployment Scripts**: Higher complexity, requires converting bash scripts to Ansible roles and playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README content
2. The Chef Automate and Chef Infra Server deployment scripts are intended for initial setup only, not ongoing configuration management
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production
4. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and don't require significant changes beyond organization into proper Ansible structure
5. Test Kitchen with Vagrant is the primary testing methodology and should be preserved or replaced with equivalent functionality