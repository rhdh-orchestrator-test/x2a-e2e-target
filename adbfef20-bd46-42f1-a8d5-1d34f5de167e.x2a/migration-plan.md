# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a standardized Ansible approach. The repository appears to be primarily a set of examples and demonstrations rather than a full production infrastructure codebase. The migration scope is relatively small, with two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing

The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the codebase is already in Ansible format.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure web server with SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website deployment
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be designed for both on-premises and cloud VMs (based on comments in the deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or alternative configuration management approach
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Consider migrating to Ansible-native testing with:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - Or retain InSpec as a testing tool while using Ansible for configuration management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for hardening Apache SSL configuration
  
- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Approach: Create an Ansible role that can either generate self-signed certificates or integrate with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: The current setup uses bash scripts to deploy Chef Automate
  - Challenge: Creating equivalent Ansible roles to replace Chef infrastructure
  - Mitigation: Create Ansible roles that focus on the configuration management aspects rather than deploying Chef itself

- **InSpec Testing**: The current setup uses InSpec for compliance testing
  - Challenge: Deciding whether to maintain InSpec or migrate to Ansible-native testing
  - Mitigation: Consider a hybrid approach where Ansible handles configuration and InSpec handles compliance testing

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Review and refactor into proper Ansible role structure
   - Update testing framework

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Integrate into a comprehensive Apache hardening role
   - Update testing framework

3. **chef-automate-deployment** (moderate complexity)
   - Determine if Chef Automate functionality is still needed
   - If yes, create Ansible roles to deploy alternative configuration management solution
   - If no, focus on migrating the underlying infrastructure configuration

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The Chef Automate and Chef Server components are intended to be replaced with Ansible equivalents
3. InSpec testing is a requirement that should be maintained or replaced with equivalent functionality
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The security hardening in the poodle_fix.yml playbook is a critical requirement
6. The self-signed certificates are acceptable for the demonstration environment but may need to be replaced with proper certificates in production
7. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with secure credential management in production