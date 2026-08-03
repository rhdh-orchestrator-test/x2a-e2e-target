# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

The estimated timeline for migration is 1-2 weeks given the limited scope and straightforward nature of the components.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with InSpec tests for deploying and validating a secure Apache web server
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.command` or `community.general.inspec` module
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that perform equivalent setup

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening in the Apache configuration
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: Maintain SSH security configurations tested by InSpec
  - Migration approach: Create an Ansible role for SSH hardening that satisfies the InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible deployments
  - Mitigation: Use Ansible's `community.general.inspec` module or call InSpec directly via `ansible.builtin.command`

- **Chef Automate Deployment**: Converting the Chef Automate deployment process to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts, with proper idempotence

### Migration Order

1. **chef-and-ansible playbooks** (low risk, already Ansible)
   - Refactor existing Ansible playbooks into proper roles
   - Integrate InSpec tests with Ansible using appropriate modules
   - Replace Test Kitchen with Molecule for testing

2. **setup-automate scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Use Ansible Vault for credential management
   - Implement proper idempotence checks

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments
2. InSpec will continue to be used for compliance testing
3. The Chef Automate/Infra Server deployment scripts are intended to be converted to Ansible rather than maintained as-is
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The target environment will continue to be Ubuntu 20.04 or similar
6. The existing Ansible playbooks are functional and follow best practices
7. No external dependencies or integrations beyond what's visible in the repository