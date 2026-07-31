# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks given the limited scope and relatively simple configurations. The complexity is low to moderate, with the main challenge being the conversion of InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks like:
  - Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - testinfra for server validation testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and management
  - Ansible Collections for role and module management
  - Git repositories for version control of playbooks

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security settings:
  - Ensure TLS 1.2+ is enforced (currently done in poodle_fix.yml)
  - Maintain self-signed certificate generation (currently using openssl_* modules)

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure PermitRootLogin is disabled
  - Convert InSpec tests to equivalent Ansible assertions or testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migration to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks:
  - Challenge: InSpec has specific resource types and matchers
  - Mitigation: Map InSpec resources to testinfra or custom Ansible modules

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents:
  - Challenge: Chef Server provides organization management and policy-based configuration
  - Mitigation: Use Ansible AWX/Tower for role-based access control and inventory management

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize existing Ansible playbook
3. **InSpec Tests** (moderate complexity): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (high complexity): Convert to Ansible playbooks for deploying alternative infrastructure

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec tests are used for validation of infrastructure rather than continuous compliance
3. There are no external dependencies on Chef Server or Chef Automate beyond what's in the setup scripts
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The migration will replace Chef InSpec with an Ansible-compatible testing framework
6. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can be used with minimal modifications
7. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with Ansible playbooks that deploy alternative infrastructure management tools