# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec for compliance testing while integrating it with pure Ansible workflows

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

- **ssh_profile**:
    - Description: Chef InSpec profile for SSH security compliance testing
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, CCI-000774 compliance check

- **website_https_verify**:
    - Description: Chef InSpec profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL/TLS protocol validation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Likely a static file for the website example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform setup
- **Chef InSpec**: Maintain as a compliance testing tool, but integrate with Ansible workflows
- **Test Kitchen**: Consider migrating to Molecule for Ansible role testing, while maintaining InSpec for verification

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should preserve:
  - Self-signed certificate generation
  - Apache SSL configuration
  - POODLE vulnerability mitigation (disabling SSLv3)
  
- **SSH Security**: The SSH InSpec profile checks for secure SSH configuration. Migration should:
  - Ensure SSH root login remains disabled
  - Maintain compliance with CCI-000774 requirements
  
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates and keys
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the bash scripts to Ansible playbooks will require:
  - Understanding Chef Automate deployment requirements
  - Creating idempotent Ansible tasks for each step
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  
- **InSpec Integration**: Ensuring Chef InSpec tests continue to work with the migrated Ansible playbooks
  - Maintaining both website_https_verify.rb and ssh_profile.rb tests
  - Integrating with Ansible-native testing frameworks

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Standardize structure and variable naming
   - Implement Ansible best practices
   
2. **poodle_fix playbook** (low risk, already Ansible)
   - Standardize structure and variable naming
   - Implement Ansible best practices
   
3. **InSpec profiles** (low risk, maintain as-is)
   - Integrate with Ansible testing workflow
   - Ensure compatibility with updated playbooks
   
4. **Chef Server/Automate deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credentials
   - Create roles for reusable components

### Assumptions

1. The repository is primarily for demonstration purposes, as indicated by the README.md mentioning "working examples" related to content created by Technical Product Marketing.
2. The Chef InSpec tests are intended to be maintained as part of the compliance strategy.
3. The existing Ansible playbooks are functional but may not follow current best practices.
4. The Chef Automate and Chef Infra Server deployment scripts are intended for educational/demonstration purposes rather than production use, given the hardcoded credentials.
5. The target environment is Ubuntu 20.04, as specified in the Test Kitchen configuration.
6. The migration goal is to standardize on Ansible while maintaining the compliance testing capabilities of Chef InSpec.