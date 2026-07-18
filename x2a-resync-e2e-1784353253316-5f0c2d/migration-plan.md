# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The primary components are:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for web server configuration with InSpec testing
3. Test Kitchen configuration for integration testing

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The main effort will be migrating the Chef server deployment scripts to Ansible roles and integrating the InSpec testing framework with pure Ansible workflows. Estimated timeline: 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying and securing Apache web servers with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for integration testing with Ansible and InSpec
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but integrate it with Ansible using the `inspec` Ansible module

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Molecule for Ansible role testing
  - Option 2: Use simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace with Ansible-based infrastructure:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Use GitLab CI/CD or Jenkins with Ansible for automation

### Security Considerations

- **SSL Configuration**: The current playbooks include SSL hardening (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Preserve these security configurations in Ansible roles
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that applies the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: The current setup uses InSpec for compliance testing
  - Challenge: Maintaining compliance testing capabilities without Chef InSpec
  - Mitigation: Either keep InSpec as a standalone tool or migrate tests to Ansible-native assertions

- **Certificate Management**: The current setup generates self-signed certificates
  - Challenge: Ensuring proper certificate management in the migrated solution
  - Mitigation: Create an Ansible role specifically for certificate management with proper security practices

### Migration Order

1. **chef-and-ansible/website_https.yml** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Add documentation

2. **chef-and-ansible/poodle_fix.yml** (low risk, already Ansible)
   - Incorporate into the web server role as a security hardening task
   - Update to include more current SSL/TLS best practices

3. **setup-automate scripts** (moderate complexity)
   - Create Ansible roles to replace the Chef server deployment scripts
   - Implement Ansible Vault for credential management

4. **Testing Framework** (high complexity)
   - Decide on testing strategy (keep InSpec or migrate to Molecule/other)
   - Implement the chosen testing framework

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
2. Compliance testing is a critical requirement that must be preserved in the migration
3. The current setup is for demonstration/example purposes and may not represent a complete production environment
4. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with secure alternatives
5. The target environment will continue to be Ubuntu-based systems
6. The team has expertise in both Chef and Ansible to facilitate the migration