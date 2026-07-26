# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for Chef Automate/Chef Infra Server deployment. The migration scope is relatively small, with only a few files to migrate. The estimated timeline for migration is 1-2 days for a skilled Ansible developer.

The repository appears to be primarily focused on examples and demonstrations rather than production infrastructure code, with two main components:
1. Chef Automate/Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing integration

## Module Migration Plan

This repository contains Ansible playbooks, Bash scripts, and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate deployment, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server deployment, user and organization creation

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Possibly a static HTML file (content not examined)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for Chef Automate deployment or consider migrating to pure Ansible infrastructure
- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec as a testing tool (Ansible can still call InSpec)
- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks
  
- **POODLE Vulnerability Mitigation**: The poodle_fix.yml playbook specifically addresses SSL security by disabling vulnerable protocols.
  - Migration approach: Maintain this security hardening in the migrated Ansible roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password, email)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: The Bash scripts for Chef Automate deployment contain specific commands and configurations that need to be translated to Ansible tasks.
  - Mitigation strategy: Create an Ansible role that performs the same steps as the Bash scripts, using Ansible modules like `command`, `lineinfile`, and `template`

- **InSpec Testing Integration**: The repository uses Chef InSpec for testing Ansible-deployed infrastructure.
  - Mitigation strategy: Either maintain InSpec as a testing tool (Ansible can execute InSpec tests) or migrate to Molecule for testing

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **deploy-automate.sh** and **deploy-chef-server.sh** (convert Bash scripts to Ansible roles, moderate complexity)
4. **website_https_verify.rb** (convert InSpec tests to Ansible Molecule tests or maintain as InSpec, moderate complexity)

### Assumptions

1. The repository is primarily for demonstration purposes rather than production infrastructure
2. The Ansible playbooks are already in a format compatible with modern Ansible versions
3. The Chef Automate and Chef Infra Server deployment scripts are intended to be migrated to Ansible rather than maintained as Chef infrastructure
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production
5. The Test Kitchen configuration is used for testing the Ansible playbooks with InSpec verification
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. The migration will maintain the same functionality as the original code
8. The InSpec tests will either be maintained as InSpec or migrated to Ansible Molecule tests