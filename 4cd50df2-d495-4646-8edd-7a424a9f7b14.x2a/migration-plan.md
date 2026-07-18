# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on infrastructure automation and compliance testing. The primary migration scope involves:

1. Chef Automate and Chef Infra Server deployment scripts
2. Chef InSpec compliance tests used alongside Ansible playbooks

The migration complexity is **LOW to MEDIUM** as the repository primarily contains deployment scripts and InSpec tests rather than complex Chef cookbooks. The estimated timeline for migration is 1-2 weeks, with the main effort focused on converting the Chef Automate/Infra Server deployment scripts to Ansible playbooks and ensuring the InSpec tests continue to work with the new Ansible implementation.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, server configuration

- **ansible-apache-https**:
    - Description: Ansible playbook for deploying Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **ansible-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration for Apache

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS and SSH compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the Apache HTTPS deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a compliance testing tool to work alongside Ansible (no migration needed)
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that accomplish the same server setup
- **Test Kitchen**: Update to use Ansible-native testing frameworks or retain with configuration updates

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the POODLE fix playbook
- **SSH Security**: Maintain SSH hardening configurations tested by the InSpec profile
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef server deployment scripts (username, password)
  - SSL certificate generation and management in the Apache HTTPS playbook
  - Recommendation: Use Ansible Vault to secure credentials in the migrated solution

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires understanding of Chef server architecture and configuration
  - Mitigation: Use the official Chef documentation to understand the deployment process and create equivalent Ansible tasks
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible implementation
  - Mitigation: Maintain the same test structure and update the Test Kitchen configuration

### Migration Order

1. **ansible-apache-https** and **ansible-poodle-fix**: Already in Ansible format, no migration needed
2. **chef-automate-deployment**: Convert Bash scripts to Ansible playbooks
3. **inspec-compliance-tests**: Ensure compatibility with the new Ansible implementation

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "companion to a white paper"
2. The InSpec tests are intended to be used with Ansible playbooks, not Chef cookbooks
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure values in a production environment
4. The Test Kitchen configuration is used for testing the Ansible playbooks with InSpec verification
5. The migration goal is to have a fully Ansible-based solution while retaining InSpec for compliance testing