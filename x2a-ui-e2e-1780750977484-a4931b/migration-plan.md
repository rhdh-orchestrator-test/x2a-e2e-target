# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web server with HTTPS
2. Chef InSpec tests for validating security compliance

The migration complexity is **LOW** as most of the infrastructure code is already in Ansible format. The primary task will be to replace Chef InSpec tests with equivalent Ansible-native testing solutions. Estimated timeline: **1-2 weeks** for a small team.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **apache-https-website**:
    - Description: Apache web server with HTTPS configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enforces TLSv1.2

- **compliance-tests**:
    - Description: InSpec tests for validating HTTPS configuration and SSH hardening
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS content verification, SSL/TLS protocol validation, SSH root login security check

- **chef-deployment**:
    - Description: Scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file for the web server - can be directly used in Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test module
  - Option 3: Ansible Lint for static analysis
  - Option 4: Integration with other testing frameworks like Serverspec or pytest

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: The deployment scripts are not directly related to the Ansible playbooks and can be:
  - Option 1: Converted to Ansible playbooks for Chef server deployment
  - Option 2: Maintained as separate bash scripts if Chef infrastructure is still needed
  - Option 3: Replaced with Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enforces TLSv1.2
  - Migration approach: Preserve the same Apache configuration in the Ansible playbooks

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented

- **SSH Hardening**: The InSpec tests validate SSH root login is disabled
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule

- **Vault/secrets management**:
  - No encrypted secrets detected in the repository
  - Hardcoded credentials found in setup-automate scripts (username, password)
  - Migration recommendation: Use Ansible Vault for credential storage

### Technical Challenges

- **Testing Framework Replacement**: Replacing Chef InSpec with Ansible-native testing
  - Mitigation: Use Molecule which provides similar functionality for infrastructure testing
  - Alternative: Use Ansible's assert module for basic compliance checks

- **Compliance Validation**: Ensuring the same level of compliance validation
  - Mitigation: Map each InSpec control to equivalent Ansible assertions or Molecule tests

### Migration Order

1. **apache-https-website** (low risk, already in Ansible)
   - Convert to Ansible role structure
   - Add documentation

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the Apache role
   - Add documentation

3. **compliance-tests** (moderate complexity)
   - Convert InSpec tests to Molecule or Ansible assertions
   - Ensure all compliance checks are preserved

4. **chef-deployment** (optional, depending on requirements)
   - Convert to Ansible playbooks if Chef infrastructure is still needed
   - Or replace with Ansible AWX/Tower setup

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef InSpec dependencies
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The self-signed certificate approach is acceptable (vs. using Let's Encrypt or other CA)
4. The Chef server deployment scripts may or may not need migration depending on whether Chef infrastructure is still required
5. No external dependencies or third-party modules are used beyond standard Ansible modules
6. The current security hardening requirements must be maintained in the migrated solution