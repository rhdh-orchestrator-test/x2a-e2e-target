# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks that are used for demonstration and educational purposes. The repository appears to be focused on showing how Chef InSpec can be used alongside Ansible for compliance automation, rather than being a production infrastructure codebase.

The migration scope is relatively small, as most of the Ansible code is already in place. The main migration effort will involve:

1. Converting the Chef Automate and Chef Infra Server setup scripts to Ansible playbooks
2. Ensuring the existing Ansible playbooks follow best practices
3. Organizing the codebase into a proper Ansible project structure

Given the limited scope, this migration could be completed in approximately 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **chef-automate-setup**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-setup**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying the HTTPS website deployment
- `index.html`: Sample HTML file for testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Vagrant**: Can be retained but updated to use Ansible-native testing approaches
- **Chef InSpec**: Can be retained as a compliance testing tool alongside Ansible

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook addresses the POODLE vulnerability by enforcing TLSv1.2. This security practice should be maintained in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. In a production environment, consider using Let's Encrypt or another trusted CA.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should follow Ansible best practices for secure key management

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible will require careful handling of the installation process, which may involve multiple steps and dependencies.
- **InSpec Integration**: Ensuring that Chef InSpec tests continue to work with the Ansible-managed infrastructure will require proper test integration.

### Migration Order

1. Create proper Ansible project structure (roles, playbooks, inventory)
2. Migrate Chef server setup scripts to Ansible playbooks (moderate complexity)
3. Refactor existing Ansible playbooks to follow best practices (low complexity)
4. Update testing framework to work with the new structure (low complexity)

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly
3. Chef InSpec will continue to be used for compliance testing alongside Ansible
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the codebase
6. The hardcoded credentials in the setup scripts are for demonstration only and not used in production