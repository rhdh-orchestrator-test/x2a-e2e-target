# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring a secure web server with HTTPS
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks**. The primary focus will be on:
- Preserving the InSpec compliance tests while migrating them to work with pure Ansible
- Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
- Ensuring the existing Ansible playbooks follow best practices

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with SSL/TLS setup, self-signed certificates, and a basic "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Deployment script for Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

- **inspec-compliance-tests**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol verification, SSH root login check

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file for the web server
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Continue using InSpec but integrate with Ansible using the `inspec` Ansible module
  - Option 2: Replace with Ansible's built-in `assert` module for basic tests
  - Option 3: Use Molecule for testing Ansible roles with testinfra as the verifier

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Create an Ansible role for Apache security hardening that includes the POODLE fix

- **Self-signed Certificates**: The current setup generates self-signed certificates
  - Approach: Create an Ansible role for certificate management with options for self-signed or Let's Encrypt certificates

- **SSH Security**: The InSpec tests verify SSH root login is disabled
  - Approach: Create an Ansible role for SSH hardening that disables root login and implements other security best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Approach: Move credentials to Ansible Vault and use variables instead of hardcoded values

### Technical Challenges

- **InSpec Integration**: Ensuring compliance testing remains effective after migration
  - Mitigation: Either maintain InSpec as a separate tool or carefully map InSpec tests to equivalent Ansible assertions

- **Chef-specific Functionality**: The Chef Automate and Chef Infra Server deployment scripts contain Chef-specific commands
  - Mitigation: Research equivalent Ansible Tower/AWX setup procedures and create roles for deployment

- **Test Kitchen to Molecule Migration**: Ensuring test scenarios are preserved
  - Mitigation: Create equivalent Molecule scenarios that match the existing Test Kitchen configuration

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Refactor according to Ansible best practices
   - Split into reusable roles (apache, ssl, website)

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate into the Apache security role
   - Enhance with additional security hardening

3. **inspec-compliance-tests** (medium complexity)
   - Either integrate InSpec with Ansible or convert to Ansible assertions
   - Create Molecule test scenarios

4. **chef-automate-deploy and chef-server-deploy** (high complexity)
   - Convert to Ansible roles for deploying AWX/Ansible Tower
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production deployment
2. The InSpec tests are essential and must be preserved in some form
3. The target environment will continue to be Ubuntu 20.04 or compatible
4. Vagrant will continue to be used for local development/testing
5. The hardcoded credentials in the deployment scripts are for demonstration only and will be replaced with secure alternatives
6. The self-signed certificates are acceptable for the demonstration environment but may need to be replaced with proper certificates in production
7. The migration will maintain the same level of security hardening present in the original configurations