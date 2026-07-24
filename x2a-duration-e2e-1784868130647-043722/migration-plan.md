# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and integrating Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks or use the ansible.builtin.assert module

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain the same level of security validation in tests

- **SSH Security**: Maintain SSH hardening checks from the InSpec profile
  - Convert the SSH root login verification to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Current implementation uses hardcoded credentials in shell scripts (username, password)
  - Migration should implement Ansible Vault for secure credential storage
  - Credentials detected: 3 (username, password, and email in deployment scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation
  - Mitigation: Use ansible.builtin.assert or custom modules to replicate InSpec functionality
  - Consider using the ansible-lint security checks as a partial replacement

- **Deployment Script Conversion**: Converting bash scripts to Ansible roles
  - Mitigation: Create dedicated roles for Chef Automate and Chef Infra Server deployment
  - Use Ansible's package management and service modules to replace curl and manual installation

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Refactor into a proper Ansible role structure
   - Add documentation and variables

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Refactor into a proper Ansible role structure or include as a task in the website role
   - Add documentation and variables

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all security checks are maintained

4. **Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential storage
   - Add proper error handling and idempotence

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The Chef InSpec tests are used for compliance validation of infrastructure configured by Ansible, not for validating Chef-managed resources.

3. The deployment scripts are intended for setting up Chef infrastructure, which may be out of scope for the Ansible migration if the goal is to move away from Chef entirely.

4. The current implementation uses hardcoded values and lacks proper variable management, which should be addressed in the migration.

5. The security configurations in the playbooks and tests represent minimum requirements that must be maintained in the migrated solution.

6. Test Kitchen is currently used for local development and testing, which will need to be replaced with an Ansible-native testing solution.