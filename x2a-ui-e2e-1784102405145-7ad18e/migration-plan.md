# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that deploy a secure web server
3. Integrating Chef InSpec tests into an Ansible-based compliance workflow

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks, as most components are already Ansible-based with InSpec tests. The primary work involves converting the Chef server deployment scripts to Ansible playbooks and ensuring the InSpec tests continue to work in the new environment.

## Module Migration Plan

This repository contains Bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **secure-web-server**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as the compliance testing framework, but integrate with Ansible using ansible-lint and Molecule
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
- **Chef Automate/Infra Server**: Replace with alternative compliance and configuration management solutions:
  - Options include: Ansible AWX/Tower for orchestration, GitLab CI for pipeline integration, or Compliance as Code approach using InSpec directly

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable vulnerable protocols
  - Migration approach: Preserve this security hardening in Ansible playbooks
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Ensure Ansible playbooks apply the same SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible workflow
  - Mitigation: Use Ansible's `verify` module or Molecule's verifier to run InSpec tests
  
- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Map Chef Server functions to Ansible Tower/AWX or other configuration management tools

### Migration Order

1. **secure-web-server** and **ssl-poodle-fix** (low risk, already Ansible)
   - Only need to update the testing framework from Test Kitchen to Molecule
   
2. **chef-automate-deployment** (moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Replace hardcoded credentials with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The Chef Automate and Chef Infra Server deployment is for demonstration purposes
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. No complex Chef cookbooks or recipes need migration (only deployment scripts)
5. InSpec will continue to be used for compliance testing after migration
6. No external dependencies or integrations beyond what's visible in the repository