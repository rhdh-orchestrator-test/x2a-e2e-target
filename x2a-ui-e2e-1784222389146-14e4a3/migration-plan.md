# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web servers with HTTPS
2. Chef InSpec tests for validating security compliance of the deployed infrastructure

The migration complexity is **LOW** as most of the code is already in Ansible format, with only the InSpec tests needing conversion to Ansible's native testing capabilities. Estimated timeline: **1-2 weeks** for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **apache-https-website**:
    - Description: Apache web server with HTTPS configuration, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enforces TLSv1.2

- **https-compliance-tests**:
    - Description: InSpec tests to verify HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, CCI compliance checks, STIG validation

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Server and Chef Automate
    - Path: setup-automate/deploy-chef-server.sh, setup-automate/deploy-automate.sh
    - Technology: Bash scripts
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file for web server testing - can be reused as-is

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Server**: The deployment scripts can be converted to Ansible roles
  - Consider whether Chef Server/Automate is still needed or if it should be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening for HTTPS:
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable protocols (SSLv3)
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile must be maintained:
  - Convert the InSpec SSH checks to Ansible assertions or Molecule tests
  - Ensure root login remains disabled

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificate generation should use Ansible's crypto modules with proper secret management

### Technical Challenges

- **Test Conversion**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a test mapping document to ensure all compliance checks are preserved

- **Integration Testing**: Ensuring the full deployment and testing workflow works end-to-end
  - Mitigation: Set up a CI/CD pipeline to validate the migrated code

### Migration Order

1. **apache-https-website** (already in Ansible format, minimal changes needed)
2. **poodle-vulnerability-fix** (already in Ansible format, minimal changes needed)
3. **https-compliance-tests** (convert from InSpec to Ansible testing)
4. **ssh-security-compliance** (convert from InSpec to Ansible testing)
5. **chef-server-deployment** (convert bash scripts to Ansible roles)

### Assumptions

1. The current setup uses Chef InSpec primarily for testing, not for configuration management
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The self-signed certificates are for testing only and would be replaced with proper certificates in production
4. The hardcoded credentials in the Chef Server deployment scripts are for demonstration purposes only
5. The migration will maintain the same level of security compliance checking
6. Test Kitchen is only used for development/testing and not for production deployments