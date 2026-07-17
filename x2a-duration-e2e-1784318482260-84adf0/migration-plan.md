# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, generates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **website-https-compliance**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Simple HTML file used as a template for website deployment - can be preserved as-is or moved to Ansible templates directory

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Consider if Chef Automate functionality is still needed or if it can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: Maintain the SSH security controls verified by the InSpec profile
  - Create equivalent Ansible tasks to enforce SSH root login restrictions

- **Certificate Management**: The self-signed certificate generation should be preserved
  - Consider enhancing with Let's Encrypt integration for production environments

- **Vault/secrets management**: 
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommend migrating these to Ansible Vault

### Technical Challenges

- **Compliance Testing**: The primary challenge will be replacing Chef InSpec with equivalent Ansible testing capabilities
  - Solution: Use a combination of Ansible assert modules and custom modules to perform the same validation

- **Test Execution Framework**: Test Kitchen provides a structured way to run tests that needs to be replaced
  - Solution: Implement Molecule for testing Ansible roles with similar capabilities

- **Maintaining Audit Trail**: InSpec provides clear compliance reporting that needs to be preserved
  - Solution: Consider integrating with Ansible Tower/AWX for reporting or maintaining InSpec as a separate tool called from Ansible

### Migration Order

1. **website-https-configuration** (low risk, already Ansible)
   - Minimal changes needed, just reorganize into proper Ansible role structure

2. **poodle-vulnerability-fix** (low risk, already Ansible)
   - Integrate with the website-https role as a security enhancement

3. **chef-automate-deployment** and **chef-server-deployment** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential storage

4. **website-https-compliance** and **ssh-security-compliance** (high complexity)
   - Develop equivalent testing functionality using Ansible-native tools
   - Ensure all compliance checks are preserved

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are considered valuable and their functionality should be preserved
3. There is no requirement to maintain Chef Automate/Infra Server functionality after migration
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The migration should consolidate all infrastructure management into Ansible
6. The self-signed certificates are acceptable (no need for CA-signed certificates)
7. The hardcoded credentials in the setup scripts are for demonstration purposes only