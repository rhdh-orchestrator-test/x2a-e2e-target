# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main focus will be on preserving the compliance testing functionality while consolidating everything into pure Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enforces TLSv1.2

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH hardening
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content testing, SSL/TLS protocol validation, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML content for the web server
- `README.md`: Documentation explaining the purpose of the examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for testing Ansible roles
  - Option 4: Keep InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for role testing
  - Or simplify to use Vagrant directly with Ansible provisioner

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enforces TLSv1.2
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL/TLS configurations

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled
  - Approach: Create an Ansible role for SSH hardening that applies the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Create custom Ansible modules or use the `assert` module with appropriate conditions

- **Chef Server Deployment**: Replacing Chef server deployment scripts with equivalent Ansible roles
  - Mitigation: Create an Ansible role that installs and configures Chef server, or replace Chef server functionality with Ansible AWX/Tower

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to a proper Ansible role with variables
   - Add documentation

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Incorporate into the Apache security role
   - Add documentation

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **chef-infrastructure-deployment** (high complexity)
   - Decide whether to maintain Chef server deployment capability or replace with Ansible AWX/Tower
   - Create Ansible roles for deployment if keeping Chef infrastructure

### Assumptions

1. The primary purpose of this repository is demonstrating compliance automation, not production deployment
2. The InSpec tests are essential and their functionality must be preserved in the Ansible migration
3. The Chef server deployment scripts may be optional if the focus shifts to pure Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. No external data sources or complex integrations are present that would complicate migration