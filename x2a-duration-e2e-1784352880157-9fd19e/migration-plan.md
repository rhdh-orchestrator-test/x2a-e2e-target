# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while integrating them into a cohesive structure
3. Maintaining Chef InSpec tests for compliance verification while integrating them with Ansible

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most functionality already in Ansible

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **ansible-apache-https**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS and SSH compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol verification, SSH root login verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website deployment
- `chef-and-ansible/website_https.yml`: Ansible playbook for HTTPS website deployment
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/README.md`: Documentation file explaining the Chef InSpec with Ansible integration
- `README.md`: Root documentation file explaining the repository purpose

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as a compliance testing tool, integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assert module where appropriate
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (POODLE fix) that must be preserved in the migration
  - Migration approach: Maintain the same configuration in Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Maintain InSpec tests and ensure Ansible playbooks configure SSH properly

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates generated during deployment
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **Chef Automate Deployment**: The current deployment uses Chef-specific CLI tools
  - Mitigation: Research and implement equivalent functionality using Ansible modules or community roles for configuration management

- **InSpec Integration**: Maintaining InSpec tests while using Ansible
  - Mitigation: Use Ansible's `shell` module to run InSpec tests or consider migrating to Ansible's native testing capabilities

### Migration Order

1. **ansible-apache-https** (already in Ansible, no migration needed)
2. **chef-automate-deployment** (convert Bash scripts to Ansible playbooks)
3. **inspec-compliance-tests** (integrate InSpec tests with Ansible or convert to Ansible assertions)

### Assumptions

1. The primary goal is to eliminate Chef-specific components while maintaining the same functionality
2. InSpec tests should be preserved for compliance verification
3. The existing Ansible playbooks are working correctly and don't need significant modifications
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The repository is primarily for demonstration/educational purposes rather than production use