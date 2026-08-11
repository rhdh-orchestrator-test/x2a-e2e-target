# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec tests for validating compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible Molecule for testing.
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration. Will need to be converted to Ansible-compatible test framework.
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Will need to be converted to Ansible-compatible test framework.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Molecule for comprehensive testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for:
  - Option 1: Deploy Chef Automate/Infra Server using Ansible (if still needed)
  - Option 2: Replace with Ansible AWX/Tower for similar functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and harden against POODLE vulnerability
  - Migration approach: Preserve the same security hardening in Ansible roles
  - Create dedicated role for Apache SSL hardening

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible role that applies the same SSH hardening
  - Add Ansible assert tasks to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules or Molecule verifiers to replicate InSpec tests
  - Consider maintaining InSpec tests if they provide value beyond what Ansible can test

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Mitigation: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Add documentation and improve variable naming

2. **poodle-fix playbook** (low risk, already Ansible)
   - Integrate into the Apache/web server role
   - Add conditional logic for different Apache versions

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate/Infra Server deployment
   - Or replace with AWX/Tower deployment playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The Apache configuration is intended for demonstration and not production use
5. The self-signed certificates are acceptable for the intended use case
6. The repository is meant as a companion to educational content rather than a standalone application