# MIGRATION FROM ANSIBLE AND CHEF SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef server setup scripts that need to be migrated to a standardized Ansible structure. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts for Chef server setup. The estimated timeline for migration is 1-2 days given the limited scope.

## Module Migration Plan

This repository contains Ansible playbooks and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: Chef InSpec tests for verifying HTTPS website functionality and security

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **chef-automate-cli**: Replace with Ansible roles for configuration management
- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Can be retained as Ansible can still use InSpec for compliance testing, or migrate to Ansible's built-in assert module for simpler tests

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible roles.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **Hardcoded Credentials**: The Chef server setup scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab

### Technical Challenges

- **Chef Server Setup**: Converting the Chef server setup scripts to Ansible will require creating roles that install and configure Chef Server components. This may require additional testing to ensure proper functionality.
- **InSpec Integration**: Ensuring that the InSpec tests continue to work with the migrated Ansible roles will require careful planning of the testing framework.

### Migration Order

1. **website_https playbook** (low risk, already Ansible): Refactor into a proper Ansible role structure
2. **poodle_fix playbook** (low risk, already Ansible): Refactor into a proper Ansible role structure
3. **Chef server deployment scripts** (moderate complexity): Convert bash scripts to Ansible roles

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.md.
2. The Chef server setup scripts are intended to be run on a fresh Ubuntu 20.04 system.
3. The current implementation assumes manual execution of scripts and playbooks rather than integration with CI/CD pipelines.
4. No external inventory or variable files are being used for the Ansible playbooks.
5. The Test Kitchen configuration is used for local testing only and not part of a larger testing framework.
6. The Chef InSpec tests are intended to be run manually or through Test Kitchen rather than as part of an automated compliance pipeline.