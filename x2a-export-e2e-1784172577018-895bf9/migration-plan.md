# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully migrate all components to pure Ansible. The primary focus will be on replacing Chef InSpec tests with Ansible-native solutions like ansible-lint and Molecule.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache virtual host configuration, SSL certificate generation, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: InSpec tests to verify HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS response verification, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Molecule for Ansible testing.
- `index.html`: Sample HTML file for website testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis of playbooks
  - Option 2: Use Molecule for integration testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Use the `community.general.apache2_module` Ansible module with appropriate parameters

- **SSH Security Hardening**: The SSH compliance tests must be maintained
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule verify phase tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation: Use Molecule's verify phase with testinfra or goss for similar functionality

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment scripts
  - Mitigation: If Chef infrastructure is still needed, maintain scripts as-is or convert to Ansible roles for Chef deployment

### Migration Order

1. **website-https-configuration** (already in Ansible, low risk)
2. **poodle-vulnerability-fix** (already in Ansible, low risk)
3. **website-https-compliance** (medium complexity, convert InSpec to Molecule)
4. **ssh-security-compliance** (medium complexity, convert InSpec to Molecule)
5. **chef-automate-deployment** and **chef-server-deployment** (high complexity, depends on whether Chef infrastructure is still needed)

### Assumptions

1. The primary goal is to migrate to pure Ansible, eliminating Chef dependencies where possible
2. InSpec tests need to be converted to Ansible-native testing solutions
3. The deployment scripts for Chef Automate and Chef Infra Server may not need migration if the infrastructure is still required
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The repository is primarily for demonstration/educational purposes rather than production use
7. Test Kitchen is used for development and testing, not for production deployments