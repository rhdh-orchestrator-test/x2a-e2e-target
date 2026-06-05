# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for web server deployment with SSL configuration
2. Chef InSpec profiles for compliance testing
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Apache web server with SSL configuration and Hello World website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule for Ansible role testing
  - Option 2: Create custom Ansible playbooks for test environment provisioning

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the Apache SSL configuration
  - Maintain TLSv1.2 requirement and SSLv3 disablement
  - Ensure proper certificate generation and management

- **SSH Hardening**: Maintain compliance with STIG requirements for SSH
  - Ensure root login remains disabled
  - Preserve audit trail capabilities

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: Replacing InSpec tests with equivalent Ansible testing mechanisms
  - Challenge: InSpec provides specialized resources for compliance testing
  - Mitigation: Use a combination of Ansible modules (uri, command, assert) to replicate tests or maintain InSpec as a separate tool

- **Certificate Management**: Ensuring proper SSL certificate generation and management
  - Challenge: Maintaining the same level of security while migrating certificate handling
  - Mitigation: Use Ansible's crypto modules (openssl_*) which are already in use in the current playbooks

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and improve variable management

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Integrate with the website_https playbook as a role or included task
   - Enhance with additional SSL hardening measures if needed

3. **InSpec tests** (medium complexity)
   - Convert to Ansible assertions or maintain as InSpec tests called from Ansible
   - Ensure all compliance checks are preserved

4. **Chef server deployment scripts** (high complexity)
   - Replace with Ansible playbooks for AWX/Tower deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. InSpec tests can be replaced with equivalent Ansible functionality
3. The deployment environment will remain similar (Ubuntu 20.04)
4. The security requirements (SSL configuration, SSH hardening) must be maintained
5. The repository is primarily for demonstration/example purposes rather than production use
6. No external Chef cookbooks or complex Chef-specific features are in use
7. The migration will include improving security practices (e.g., removing hardcoded credentials)