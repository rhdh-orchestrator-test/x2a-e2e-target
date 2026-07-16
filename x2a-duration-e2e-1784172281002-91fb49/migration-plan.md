# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring a secure HTTPS website
2. Chef InSpec test profiles for validating compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-compliance-tests**:
    - Description: Chef InSpec profile for validating HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol validation

- **ssh-compliance-tests**:
    - Description: Chef InSpec profile for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, CCI compliance checks

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSLv3)

- **SSH Hardening**: Maintain the SSH security controls validated by the InSpec profile
  - Disable root login
  - Maintain compliance with security requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: jtonello, password: password)
  - Self-signed certificates generated in the website_https.yml playbook
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing capabilities currently provided by Chef InSpec
  - Solution: Evaluate ansible-lint, OpenSCAP integration, or continue using InSpec as a standalone tool called from Ansible

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Solution: Migrate to Molecule for testing Ansible roles and playbooks

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to an Ansible role for better reusability

2. **poodle-fix playbook** (low risk, already Ansible)
   - Integrate with the website-https role as a security enhancement

3. **InSpec compliance tests** (moderate complexity)
   - Evaluate options for compliance testing in Ansible
   - Either convert to ansible-lint rules or maintain as InSpec tests called from Ansible

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible playbooks for deploying compliance tools
   - Consider whether Chef Automate/Server is still needed or if it can be replaced with Ansible Automation Platform

### Assumptions

1. The primary goal is standardizing on Ansible while maintaining compliance capabilities
2. The Chef InSpec tests are valuable and should be preserved in some form
3. The Chef Automate and Chef Server deployment scripts may be obsolete if moving entirely to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (CCI-000774, etc.) must be maintained in the new implementation
7. The repository is primarily for demonstration purposes rather than production use