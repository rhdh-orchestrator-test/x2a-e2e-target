# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

Given the limited scope, this migration is estimated to be **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS**.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible's built-in assert module where appropriate
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests validate SSH security configurations. Maintain these tests and implement equivalent Ansible tasks
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates in the Ansible playbook
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec Integration**: Determine whether to maintain InSpec for compliance testing or migrate to native Ansible solutions
  - Mitigation: Keep InSpec for compliance testing as it provides specialized security testing capabilities
  
- **Chef Automate Replacement**: Identify appropriate replacement for Chef Automate functionality
  - Mitigation: Evaluate Ansible Automation Platform or AWX as alternatives

### Migration Order

1. **chef-and-ansible playbooks** (low risk, already in Ansible format)
   - Refactor existing Ansible playbooks to follow best practices
   - Convert Test Kitchen configuration to Ansible Molecule

2. **setup-automate scripts** (moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

3. **InSpec tests** (optional)
   - Either maintain as-is with Ansible integration or
   - Convert to Ansible assert modules where appropriate

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. InSpec tests are valuable and should be maintained for compliance validation
3. The Chef Automate and Chef Infra Server deployments need to be replaced with equivalent Ansible functionality
4. The hardcoded credentials in the setup scripts are for demonstration only and will be replaced with secure alternatives
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The existing Ansible playbooks are functional and follow reasonable practices
7. No external dependencies or integrations beyond what's visible in the repository