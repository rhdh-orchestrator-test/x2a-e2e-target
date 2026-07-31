# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks used for demonstration and educational purposes. The migration scope is relatively small, focusing on:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for website HTTPS configuration and SSL security fixes
3. InSpec tests for verification

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the Chef server deployment scripts into Ansible playbooks while maintaining the existing Ansible configurations.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, disabling vulnerable protocols

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS configuration
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec Tests**: Convert to Ansible-native testing frameworks like Molecule or maintain as InSpec tests

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (poodle_fix.yml) that must be preserved in the migration
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates that should be maintained or improved
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require creating roles and playbooks that accomplish the same server setup
- **InSpec Test Integration**: Ensuring that the existing InSpec tests continue to work with the migrated Ansible playbooks
- **Configuration Consistency**: Maintaining the same configuration outcomes while migrating from bash scripts to Ansible playbooks

### Migration Order

1. **website-https-configuration** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Update to use Ansible best practices if needed
   - Ensure InSpec tests continue to work

2. **ssl-poodle-fix** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Potentially merge with website-https-configuration as a role

3. **chef-automate-deployment** (moderate complexity)
   - Create Ansible roles to replace the bash scripts
   - Implement Ansible Vault for credential management
   - Test deployment thoroughly

### Assumptions

1. The repository is primarily for educational/demonstration purposes and not a production environment
2. The InSpec tests are intended to be maintained as part of the compliance strategy
3. The Chef server deployment scripts are the primary targets for migration to Ansible
4. No actual Chef cookbooks exist in this repository that need migration
5. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already well-structured and may only need minor updates
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. The deployment will continue to use Vagrant for testing purposes