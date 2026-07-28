# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on converting the Chef server setup scripts to Ansible and ensuring the existing Ansible playbooks are properly integrated into the new structure. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains both Chef server setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-setup**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

- **website-https**:
    - Description: Ansible playbook for setting up a secure web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance
- `deploy-automate.sh`: Bash script for deploying Chef Automate with Chef Infra Server
- `deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with AWX/Ansible Tower or other Ansible management solution
- **Test Kitchen**: Migrate to Molecule for Ansible role testing
- **InSpec**: Consider migrating to Ansible's built-in assert module or maintaining InSpec for compliance testing

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration which must be preserved
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: The repository uses InSpec for compliance testing alongside Ansible
  - Mitigation: Either maintain InSpec as a compliance tool or migrate tests to Ansible's native assertion capabilities

- **Chef Server Deployment**: The bash scripts deploy Chef Server components
  - Mitigation: Create Ansible roles that perform equivalent setup of a centralized configuration management system (Ansible Tower/AWX)

### Migration Order

1. **chef-automate-setup** (moderate complexity): Convert bash scripts to Ansible roles for infrastructure setup
2. **website-https** (low risk): Already in Ansible format, just needs integration into the new structure
3. **poodle-fix** (low risk): Already in Ansible format, just needs integration into the new structure
4. **InSpec Tests** (moderate complexity): Either maintain as-is or convert to Ansible assertions

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are intended to be run against systems managed by either Chef or Ansible
3. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced in production
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The migration will maintain the same functionality but consolidate on Ansible as the single configuration management tool
6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already production-ready and only need integration into the new structure