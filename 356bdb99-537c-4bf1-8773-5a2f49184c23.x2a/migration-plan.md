# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Chef Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks that are already using Chef InSpec for compliance testing

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single developer to complete. The repository appears to be primarily educational/demonstration content rather than production infrastructure code.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a compliance testing tool, which is already integrated with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Vagrant**: Can be retained for local testing or replaced with Docker for faster testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH compliance profile must be integrated into the Ansible workflow
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, possibly with ansible-vault or external certificate management

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef Automate and Chef Infra Server installation
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  - Managing user and organization creation
  - Potentially using Ansible's uri module to interact with Chef APIs

- **InSpec Integration**: Ensuring that the existing InSpec tests continue to work with the new Ansible roles
  - Consider using the ansible_inspec collection or community.general.inspec module

### Migration Order

1. **apache-https-website** (already in Ansible, just needs refinement)
2. **ssl-poodle-fix** (already in Ansible, just needs refinement)
3. **chef-automate-deployment** (requires conversion from Bash to Ansible)

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The Chef InSpec tests should be preserved as they demonstrate compliance automation
3. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with secure alternatives
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The migration will maintain the same functionality but improve security and maintainability