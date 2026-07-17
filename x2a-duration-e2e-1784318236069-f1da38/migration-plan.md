# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and securing Apache web servers
2. Chef InSpec tests for validating security compliance

The migration complexity is **LOW** as most of the content is already in Ansible format, with only the InSpec tests needing conversion to Ansible-native testing solutions. Estimated timeline: **1-2 weeks** for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks and InSpec tests for web server deployment and compliance validation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache installation, SSL configuration, security compliance testing

- **chef-and-ansible-tests**:
    - Description: InSpec tests for validating web server security and compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSH security compliance testing, STIG compliance checks

- **setup-automate**:
    - Description: Scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/index.html`: Sample HTML file for the web server deployment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible-lint for static analysis
  - Option 3: Custom Ansible playbooks with assert modules for compliance checks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: If these are only used for testing/demo purposes, replace with:
  - Ansible AWX/Tower for centralized management
  - Ansible Collections for role management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the current playbooks:
  - Ensure TLSv1.2 is enforced
  - Ensure SSL3 is disabled
  - Maintain proper certificate generation and management

- **SSH Security**: Maintain SSH hardening requirements:
  - Ensure root login remains disabled
  - Preserve STIG compliance requirements

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef server deployment scripts
  - Migration should use Ansible Vault for securing:
    - User passwords in the Chef server deployment scripts (currently hardcoded as 'password')
    - Any SSL private keys or certificates

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Mapping InSpec resources to Ansible modules
  - Ensuring the same level of compliance validation
  - Solution: Use Ansible's assert module with appropriate conditions to validate the same compliance requirements

- **Test Kitchen Integration**: Replacing Test Kitchen with Ansible Molecule:
  - Requires rewriting test configurations
  - May need to adjust how tests are executed
  - Solution: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

### Migration Order

1. **chef-and-ansible** (main module, contains Ansible playbooks that are already in the correct format)
2. **chef-and-ansible-tests** (convert InSpec tests to Ansible assertions, moderate complexity)
3. **setup-automate** (convert bash scripts to Ansible roles, high complexity)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef server and Automate deployment scripts are included as examples and may not be essential to the core functionality.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests are important and must be maintained in the Ansible migration.
5. The current implementation uses self-signed certificates for HTTPS, which is acceptable for the migration.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with Ansible Vault in the migration.