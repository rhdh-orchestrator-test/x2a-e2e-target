# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstration and example purposes. The primary content consists of:

1. Ansible playbooks for configuring HTTPS websites with InSpec tests for validation
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks that need standardization and Chef deployment scripts that need to be converted to Ansible. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks and medium complexity for the Chef server deployment scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test file for validating HTTPS website configuration
- `index.html`: Sample HTML file used in examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for Chef Automate deployment or consider if Chef Automate is still needed
- **InSpec**: Continue using InSpec for compliance testing, but integrate with Ansible using the ansible_inspec module
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt Test Kitchen to work with pure Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 only, which should be maintained or updated to include TLS 1.3
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider using Let's Encrypt in production
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username, password, and email in deploy-automate.sh and deploy-chef-server.sh
  - Count: 2 scripts with 5 credential-related variables each

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require creating roles and playbooks that perform equivalent operations
- **InSpec Integration**: Ensuring that InSpec tests continue to work with the migrated Ansible playbooks
- **Testing Framework**: Setting up a proper testing framework for the migrated Ansible content

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Standardize and improve the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Standardize and improve the existing Ansible playbook
3. **chef-server-deploy.sh** (medium complexity): Convert to Ansible role and playbook
4. **chef-automate-deploy.sh** (high complexity): Convert to Ansible role and playbook or evaluate if needed

### Assumptions

1. The repository is primarily for demonstration purposes and not production use
2. The InSpec tests should be preserved as they demonstrate compliance automation
3. The Chef deployment scripts are intended to be converted to Ansible rather than preserved
4. The target environment will continue to be Ubuntu 20.04 or newer
5. The hardcoded credentials in the scripts are for demonstration only and will be replaced with Ansible Vault
6. The self-signed certificates are acceptable for demonstration but would be replaced with proper certificates in production