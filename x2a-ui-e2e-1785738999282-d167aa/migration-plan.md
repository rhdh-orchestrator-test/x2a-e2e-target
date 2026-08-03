# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a standardized structure
3. Preserving the InSpec testing capabilities within an Ansible framework

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible_inspec` module or similar approach

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates; consider using Let's Encrypt in the Ansible migration
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - SSL certificate and key management
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture and configuration
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible structure
- **SSL Certificate Management**: Ensuring proper handling of SSL certificates in the migrated Ansible playbooks

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Standardize the playbook structure
   - Move variables to separate vars files
   - Implement Ansible Vault for sensitive data

2. **ssl-poodle-vulnerability-fix** (low risk, already in Ansible)
   - Standardize the playbook structure
   - Consider merging with the website-https-configuration as a role

3. **chef-automate-deployment** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credentials
   - Test thoroughly to ensure equivalent functionality

### Assumptions

1. The current Chef Automate and Chef Infra Server deployment is used for managing infrastructure that will also be migrated to Ansible
2. The InSpec tests are valuable and should be preserved in the migration
3. The repository is a demonstration/example repository rather than a production environment
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distribution
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives
7. The Apache configuration is a simple example and not a complex production setup