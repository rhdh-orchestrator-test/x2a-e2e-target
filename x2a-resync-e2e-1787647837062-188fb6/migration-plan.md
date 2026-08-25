# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

Given the limited scope and the fact that part of the repository already uses Ansible, this migration is estimated to be of **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS**.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for deploying and validating a secure HTTPS website
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: SSL/TLS configuration, Apache web server setup, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, as it's compatible with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative Ansible management solution

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3 to prevent POODLE vulnerability
  - Migration approach: Maintain the same security hardening in Ansible playbooks
  
- **SSH Security**: InSpec tests validate SSH root login is disabled
  - Migration approach: Maintain InSpec tests and ensure Ansible playbooks enforce the same SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates generated in playbooks
  - Migration approach: Replace hardcoded credentials with Ansible Vault or external secrets management

### Technical Challenges

- **Chef InSpec Integration**: Ensuring continued integration of InSpec tests with pure Ansible workflow
  - Mitigation: Use Ansible's built-in capabilities to run InSpec tests or integrate with CI/CD pipeline

- **Chef Automate Replacement**: Determining appropriate Ansible management platform
  - Mitigation: Evaluate Ansible Automation Platform or alternative open-source solutions based on requirements

### Migration Order

1. **chef-and-ansible module** (low risk, already using Ansible)
   - Update existing Ansible playbooks to follow best practices
   - Replace Test Kitchen with Ansible Molecule for testing
   - Maintain InSpec tests for compliance validation

2. **setup-automate module** (moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Replace hardcoded credentials with Ansible Vault
   - Implement idempotent deployment of management platform

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, as indicated by the README.md
2. Chef InSpec is being used alongside Ansible for compliance testing and should be maintained
3. The setup-automate scripts are used for deploying Chef Automate and Chef Infra Server in lab environments
4. The security configurations in the Ansible playbooks are based on industry best practices
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data migration is required as this appears to be infrastructure code only