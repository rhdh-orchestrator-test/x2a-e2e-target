# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks with the Chef deployment scripts
3. Standardizing the approach to infrastructure deployment and testing

Given the limited scope and the fact that some components are already in Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks** for a single engineer.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a simple HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **compliance-testing**:
    - Description: Chef InSpec tests for SSH hardening and HTTPS website verification
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS port and protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy only Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Maintain InSpec but integrate with Ansible using the ansible_inspec module

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for orchestration
  - AWX/Tower for web UI and API
  - Git repositories for version control of playbooks

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLSv1.2 and disable older protocols. This should be maintained in the Ansible migration.
  - Migration approach: Use the same Apache configuration but with Ansible's apache2_module and template modules

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates generated in website_https.yml
  - Migration approach: Use Ansible Vault for credential storage and ansible-vault encrypt_string for sensitive variables

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Consider using Molecule which supports multiple verifiers including InSpec, or maintain InSpec as a separate testing tool

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles that perform the same functions as the bash scripts, using Ansible modules for package installation and service configuration

### Migration Order

1. **website-https-deployment** (already in Ansible, low risk)
2. **ssl-poodle-fix** (already in Ansible, low risk)
3. **compliance-testing** (medium complexity, requires framework decision)
4. **chef-automate-deployment** (highest complexity, requires replacing Chef-specific functionality)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating these are examples related to blog content.
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, not for testing Chef cookbooks.
3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in production.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The migration will maintain the same functionality but standardize on Ansible as the single automation tool.