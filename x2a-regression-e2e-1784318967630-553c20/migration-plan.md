# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Chef Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The estimated timeline for this migration is 1-2 weeks, with low to medium complexity. The primary challenge will be replacing Chef InSpec with Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH security compliance checks

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - needs to be replaced with Ansible-native testing framework like Molecule
- `index.html`: Sample HTML file for website testing - can be reused in Ansible playbooks

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile tests must be implemented as Ansible tasks
  - Disable root login via SSH
  - Implement CIS/STIG compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Create equivalent tests using Ansible's assert module or Molecule verifiers

- **Chef Server Deployment**: Replacing Chef Automate and Chef Infra Server with Ansible-managed infrastructure
  - Mitigation: Determine if Chef Server functionality is still needed or if it can be replaced entirely with Ansible

### Migration Order

1. **apache-https-website** (low risk, already in Ansible)
   - Consolidate website_https.yml into an Ansible role
   - Convert InSpec tests to Ansible assertions or Molecule tests

2. **ssl-poodle-fix** (low risk, already in Ansible)
   - Integrate poodle_fix.yml into the Apache HTTPS role
   - Ensure tests validate the security hardening

3. **chef-automate-deployment** (moderate complexity)
   - Convert bash scripts to Ansible roles for infrastructure deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The Chef Automate and Chef Infra Server deployment is still needed and cannot be entirely replaced by Ansible
2. The InSpec tests are critical for compliance and must be maintained in some form
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The repository is primarily used for demonstration/example purposes rather than production deployment
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data migration is required as this appears to be infrastructure code only
7. The existing Ansible playbooks are functional and follow best practices
8. No CI/CD pipeline integration is present that would need to be updated