# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on two main components:

1. Chef server deployment scripts (Bash)
2. Ansible playbooks with Chef InSpec tests

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer. The primary focus will be on converting the Chef server deployment scripts to Ansible playbooks and ensuring the existing Ansible playbooks follow best practices.

## Module Migration Plan

This repository contains Ansible playbooks and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test to verify HTTPS configuration and security
- `chef-and-ansible/index.html`: Sample HTML file for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible modules for configuration management
  - Migration strategy: Create Ansible roles to handle the installation and configuration of services
  
- **Chef InSpec (version not specified)**: Keep for testing but integrate with Ansible
  - Migration strategy: Maintain InSpec tests but call them from Ansible using the `ansible.builtin.command` module or consider migrating to Ansible's built-in testing capabilities

- **Test Kitchen with Vagrant**: Consider replacing with Ansible Molecule for testing
  - Migration strategy: Create equivalent Molecule scenarios for testing Ansible roles

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols
  - Migration approach: Maintain this security hardening in the Ansible roles, consider updating to include TLSv1.3
  
- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Consider adding support for Let's Encrypt certificates as an option

- **Vault/secrets management**:
  - Hardcoded credentials in Bash scripts (username, password, email)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to idempotent Ansible playbooks
  - Mitigation strategy: Create a dedicated Ansible role for Chef server deployment with proper state checking
  
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible roles
  - Mitigation strategy: Create a testing framework that allows Ansible to call InSpec tests or migrate to native Ansible testing

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** (high value, moderate complexity)
   - Convert Bash scripts to Ansible roles
   - Implement Ansible Vault for credential storage
   
2. **website-https** (low risk, already in Ansible)
   - Refactor to follow Ansible best practices
   - Organize into proper roles and use variables
   
3. **poodle-fix** (low risk, already in Ansible)
   - Integrate into the website-https role as an optional security enhancement
   - Update to include more current security best practices

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec tests are intended to be kept as part of the compliance verification strategy
3. The target environment is Ubuntu 20.04, but the solution should be adaptable to other distributions
4. The hardcoded credentials in the scripts are for demonstration purposes and will be replaced with secure alternatives
5. The current Ansible playbooks do not follow all best practices and will benefit from refactoring
6. The migration will maintain backward compatibility with existing test frameworks
7. No external dependencies or integrations beyond what's visible in the repository need to be considered