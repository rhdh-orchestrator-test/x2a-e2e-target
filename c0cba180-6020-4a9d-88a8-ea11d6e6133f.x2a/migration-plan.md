# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the Chef InSpec tests for compliance validation

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** due to the limited number of components and straightforward functionality.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring HTTPS on a web server with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy only Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing frameworks
- **InSpec**: Maintain as a compliance testing tool, which works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance security settings:
  - Ensure TLSv1.2 or higher is enforced (as in poodle_fix.yml)
  - Maintain proper certificate generation and management
  
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement:
  - Ensure Ansible playbooks enforce the same SSH hardening measures
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, possibly with ansible-vault or external secret management

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires:
  - Creating Ansible roles for Chef Automate installation
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  - Managing user and organization creation
  
- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible:
  - Ensure InSpec tests continue to work with Ansible-managed systems
  - Consider adding Ansible-native testing alternatives like Molecule

### Migration Order

1. **website-https-configuration** (Priority 1): Already an Ansible playbook, just needs review and potential enhancement
2. **poodle-vulnerability-fix** (Priority 1): Already an Ansible playbook, just needs review and potential enhancement
3. **chef-automate-deployment** (Priority 2): Convert Bash scripts to Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md
2. The InSpec tests are intended to be maintained as they provide compliance validation
3. The Chef Automate and Chef Infra Server deployment is a key component that needs to be replaced with equivalent Ansible functionality
4. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with secure credential management in production
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
6. The migration will maintain the same functionality but implement it using Ansible best practices