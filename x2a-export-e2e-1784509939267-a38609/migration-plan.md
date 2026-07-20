# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec compliance testing

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the Chef Automate deployment scripts to Ansible playbooks while preserving the existing Ansible playbooks and enhancing the InSpec testing framework integration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec integration for compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing with InSpec
    - Components:
      - Ansible playbooks for Apache HTTPS website deployment
      - SSL/TLS security configuration
      - InSpec tests for compliance verification
      - Test Kitchen configuration for testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation
    - Components:
      - Script for deploying Chef Automate with Chef Infra Server
      - Script for deploying Chef Infra Server only
      - User and organization creation automation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as a compliance testing tool, integrate with Ansible using the `ansible.builtin.shell` module or dedicated Ansible modules for InSpec
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Apache2**: Maintain configuration management for web server in Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated Ansible playbooks.
- **SSH Security**: The InSpec profile checks for SSH root login restrictions. This compliance check should be maintained.
- **Self-signed Certificates**: The playbooks generate self-signed certificates for Apache. Consider implementing a more robust certificate management solution.
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Self-signed SSL certificates generated in the Ansible playbook
  - Recommend using Ansible Vault for credential storage in the migrated solution

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require creating roles for Chef Automate installation and configuration.
  - Mitigation: Create dedicated Ansible roles for Chef Automate and Chef Infra Server deployment, or consider replacing with pure Ansible solution if Chef is no longer needed.
  
- **InSpec Integration**: Maintaining the InSpec testing framework integration with Ansible.
  - Mitigation: Use Ansible's `community.general.inspec` module or create a custom module for InSpec integration.

- **SSL/TLS Security**: Ensuring proper SSL/TLS configuration in the migrated Ansible playbooks.
  - Mitigation: Create dedicated roles for SSL/TLS configuration with appropriate security settings.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Maintain existing playbooks with minor improvements
   - Enhance with Ansible best practices (roles, variables, etc.)
   - Migrate `website_https.yml` and `poodle_fix.yml` to proper Ansible roles

2. **Chef Deployment Scripts** (Moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Create roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential management

3. **Testing Framework** (Low complexity)
   - Migrate from Test Kitchen to Molecule for Ansible testing
   - Maintain InSpec tests and enhance integration with Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md mentioning "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which may be replaced entirely by Ansible or maintained as a hybrid solution.

3. The InSpec testing framework is valued for its compliance testing capabilities and should be preserved in the migrated solution.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. The hardcoded credentials in the deployment scripts are for demonstration purposes and should be replaced with secure credential management in the production environment.

6. The migration goal is to standardize on Ansible while maintaining the compliance testing capabilities of InSpec.