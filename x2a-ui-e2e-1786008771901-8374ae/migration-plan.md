# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, primarily focused on demonstration and example purposes. The repository includes Ansible playbooks for configuring HTTPS websites and Chef server/Automate deployment scripts. The migration scope is relatively small, with only a few playbooks and scripts to migrate. Given the limited complexity, this migration could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: Chef InSpec tests for verifying HTTPS website configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Can be retained for testing Ansible playbooks or replaced with Molecule
- **InSpec**: Can be retained for compliance testing of Ansible-managed systems

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Migration approach: Create an Ansible role for Apache security hardening
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Create an Ansible role for certificate management with options for self-signed or proper CA certificates

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality
  - Mitigation: Evaluate Ansible AWX/Tower as a replacement for Chef Server's centralized management

- **InSpec Integration**: Ensuring continued compliance testing with InSpec alongside Ansible
  - Mitigation: Document integration patterns for running InSpec tests against Ansible-managed nodes

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Integrate into the Apache security role

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The InSpec tests are intended to be run against systems managed by either Chef or Ansible
3. The deployment scripts are meant for setting up Chef infrastructure, which would be replaced by Ansible infrastructure
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The migration is focused on moving to a pure Ansible environment rather than maintaining Chef components