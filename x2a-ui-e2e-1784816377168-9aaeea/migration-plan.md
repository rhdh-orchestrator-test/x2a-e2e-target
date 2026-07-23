# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks with Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but proper integration of compliance testing in the new Ansible structure requires careful planning.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for Apache

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Replace with:
  - **Option 1**: Continue using InSpec with Ansible (recommended for compliance-heavy environments)
  - **Option 2**: Migrate to Ansible's built-in assert module and custom modules for simpler tests
  - **Option 3**: Use alternative compliance tools like Ansible Lint or Molecule for testing

- **Test Kitchen with kitchen-ansible**: Currently used for testing. Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening must be preserved in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with configurable SSL/TLS parameters

- **SSH Hardening**: The InSpec tests verify SSH security configurations (disabling root login).
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Create an Ansible role for certificate management with options for self-signed or proper CA-signed certificates

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing Integration**: Maintaining the compliance testing capabilities while migrating to pure Ansible.
  - Mitigation: Either keep InSpec for testing or develop equivalent tests using Ansible's native capabilities

- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Server deployment need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment, or consider if this is still needed in an Ansible-only environment

### Migration Order

1. **website_https playbook** (low risk, high value) - Convert to an Ansible role with proper structure
2. **poodle_fix playbook** (low risk) - Integrate into the Apache role as a security hardening task
3. **InSpec tests** (moderate complexity) - Either keep as-is or convert to Ansible-native testing
4. **Chef deployment scripts** (high complexity) - Convert to Ansible roles if still needed

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the compliance testing capabilities
2. The Chef Automate and Chef Server deployment scripts may not be needed in an Ansible-only environment
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
5. Test Kitchen can be replaced with Ansible Molecule for testing
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with secure credential management