# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance requirements

Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook to fix SSL/TLS vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol testing, SSH root login security check

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used for testing the web server - can be reused in Ansible

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - CI/CD pipeline integration for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Use Ansible's `lineinfile` or `template` modules to manage Apache SSL configuration

- **SSH Security**: Maintain compliance checks for SSH root login restrictions
  - Approach: Convert InSpec tests to Ansible assertions or continue using InSpec as a compliance tool

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **Testing Framework Migration**: Converting from InSpec to Ansible-native testing
  - Mitigation: Consider using Molecule for testing Ansible roles and playbooks, or keep InSpec as a complementary tool

- **Certificate Management**: Ensuring secure certificate generation and management
  - Mitigation: Use Ansible's `openssl_*` modules (already in use) with proper secret management

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Implement AWX/Tower for UI and job scheduling, integrate with existing CI/CD tools

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to proper Ansible role structure
   - Implement variable management
   - Add documentation

2. **poodle-fix** (low risk, already in Ansible)
   - Integrate with the website-https role
   - Improve idempotency
   - Add documentation

3. **compliance-tests** (medium complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Maintain compliance reporting capabilities

4. **chef-deployment** (high complexity)
   - Create Ansible playbooks for AWX/Tower deployment
   - Implement secure credential management
   - Document migration path for existing Chef users

### Assumptions

1. The current setup uses Chef InSpec primarily for testing, not for configuration management
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. The deployment scripts are for setting up a new Chef environment, not migrating an existing one
4. There are no external dependencies or integrations not visible in the repository
5. The security requirements (TLS 1.2, SSH restrictions) must be maintained in the migrated solution
6. The self-signed certificates are for testing only and not production use
7. No database or complex application dependencies exist beyond what's visible in the code
8. The migration will be to pure Ansible without maintaining Chef components