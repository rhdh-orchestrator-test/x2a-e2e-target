# MIGRATION FROM ANSIBLE AND CHEF SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef server setup scripts that need to be migrated to a standardized Ansible structure. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a complete migration.

The repository primarily consists of:
1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Bash scripts for deploying Chef Automate and Chef Infra Server
3. InSpec tests for verifying website HTTPS functionality

## Module Migration Plan

This repository contains Ansible playbooks and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, creates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, Apache and SSH service restart

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website functionality and security

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Can be retained for testing, as it works well with Ansible
- **Apache 2.4.41**: Continue using in Ansible playbooks with version pinning
- **OpenSSL**: Continue using in Ansible playbooks for certificate generation

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only. This should be maintained or enhanced to include TLSv1.3 in the migrated Ansible roles.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Hardcoded Credentials**: The Chef server setup scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab
  - Organization: lab

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible roles will require knowledge of Chef server architecture and configuration. Consider using the official Chef Ansible roles if available.
- **InSpec Integration**: Ensuring that InSpec tests continue to work with the new Ansible structure. This can be addressed by maintaining the same output structure and using Ansible's testing frameworks.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Move variables to defaults/main.yml
   - Create templates for Apache configuration

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Consider merging with website_https role as an optional security enhancement

3. **Chef server deployment scripts** (moderate complexity)
   - Create Ansible roles for Chef server deployment
   - Move credentials to Ansible Vault
   - Create templates for Chef server configuration

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md.
2. The InSpec tests are intended to be run as part of a CI/CD pipeline or manually after deployment.
3. The hardcoded credentials in the Chef server deployment scripts are examples and not used in production.
4. The target environment is Ubuntu 20.04, as specified in kitchen.yml.
5. The Apache version (2.4.41-4ubuntu3.10) is specifically required and should be maintained in the migration.
6. The SSL/TLS configuration is a critical security requirement and must be maintained or enhanced.
7. The Chef server deployment scripts are intended to be run on a fresh VM with no existing Chef installation.