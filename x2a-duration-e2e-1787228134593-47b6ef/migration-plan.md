# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with InSpec testing for HTTPS website deployment and SSL security fixes

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main effort will involve converting the Chef Automate deployment scripts to Ansible playbooks and ensuring the existing Ansible playbooks conform to best practices.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart handlers

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

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant and InSpec
- `tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website deployment and SSL configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Chef Server CLI**: Replace with Ansible roles for configuration management platform deployment
- **Test Kitchen**: Consider migrating to Ansible Molecule for testing or maintain Test Kitchen with Ansible driver
- **InSpec**: Can be maintained as a testing framework with Ansible, as demonstrated in the existing setup

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (poodle_fix.yml) that must be preserved in the migrated solution
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates that should be replaced with a more robust certificate management approach
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely, potentially with ansible-vault

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require creating roles and playbooks that can properly install and configure Chef Automate or an alternative configuration management platform
- **InSpec Integration**: Ensuring that InSpec tests continue to work with the migrated Ansible playbooks
- **SSL Certificate Management**: Implementing a more secure approach to certificate management than the current self-signed certificates

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Improve SSL certificate management
   - Ensure InSpec tests continue to work

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Consider integrating with the website-https playbook as a role

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles for deploying configuration management platforms
   - Implement secure credential management with Ansible Vault
   - Develop tests to verify successful deployment

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, as indicated by the README.md
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with Ansible equivalents rather than maintaining Chef infrastructure
3. The InSpec testing framework should be preserved as it works well with Ansible
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives
5. The target environment is Ubuntu 20.04 running on Vagrant VMs or generic cloud instances
6. The migration will focus on improving security practices while maintaining the same functionality