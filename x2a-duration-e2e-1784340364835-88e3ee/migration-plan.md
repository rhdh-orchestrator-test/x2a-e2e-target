# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Chef Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be standardized and integrated into a unified Ansible framework

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer. The primary challenge will be replacing the Chef InSpec testing framework with an Ansible-native testing solution while maintaining the same compliance validation capabilities.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL configuration hardening, disabling vulnerable protocols

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login security check

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for the Apache web server
- `chef-and-ansible/README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Implement custom Ansible assertion tasks to validate the same conditions

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Ansible Collections for configuration management

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security validation

- **SSH Security**: Preserve the SSH root login restrictions validated by the InSpec tests
  - Implement equivalent Ansible tasks to enforce SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, possibly using ansible-vault for private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-native validation
  - Mitigation: Use Ansible's uri module to replace HTTP validation tests and command/shell modules with assert for other validations

- **Maintaining Compliance Validation**: Ensuring the same level of compliance checking without InSpec
  - Mitigation: Document each compliance check and implement equivalent Ansible tasks

- **SSL Certificate Management**: Ensuring proper handling of SSL certificates
  - Mitigation: Use Ansible's openssl_* modules (already in use in the existing playbooks)

### Migration Order

1. **apache-https-website** (low risk, already in Ansible)
   - Standardize variable naming
   - Add documentation
   - Implement idempotency improvements

2. **ssl-poodle-fix** (low risk, already in Ansible)
   - Integrate with the apache-https-website playbook
   - Improve handler naming for consistency

3. **inspec-compliance-tests** (moderate complexity)
   - Convert to Ansible-native tests
   - Integrate with the main playbooks

4. **chef-automate-deployment** (high complexity)
   - Create new Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement variable management with Ansible Vault
   - Add proper error handling and idempotency

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies, not to maintain the Chef Automate/Infra Server infrastructure.
2. The InSpec tests are critical for compliance validation and equivalent functionality must be maintained.
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
4. The migration will preserve all security hardening measures present in the original code.
5. No additional features beyond what exists in the current repository are required.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives.
7. The Apache configuration details (virtual host settings, SSL parameters) must be preserved exactly as they are.