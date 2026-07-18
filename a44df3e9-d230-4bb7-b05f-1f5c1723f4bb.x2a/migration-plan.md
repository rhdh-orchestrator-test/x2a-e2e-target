# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 days given the limited scope.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-setup**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in assert module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec tests but run them from Ansible using the command module

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain compliance with security standards referenced in InSpec tests (SRG-OS-000112, V-38607)

- **SSH Security**: Maintain SSH hardening configurations
  - Ensure root login remains disabled as verified by the InSpec test

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in setup-automate/deploy-automate.sh and setup-automate/deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks
  - Challenge: Ensuring idempotent installation of Chef components
  - Mitigation: Use Ansible's package, command, and shell modules with appropriate conditionals

- **InSpec Test Integration**: Maintaining compliance testing capabilities
  - Challenge: Preserving the compliance testing functionality currently provided by InSpec
  - Mitigation: Either convert InSpec tests to Ansible assertions or create a wrapper playbook to run InSpec tests

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Only needs review and potential refactoring to follow best practices
   - Update to use Ansible Vault for any sensitive information

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Only needs review and potential refactoring to follow best practices

3. **Chef Automate Setup Scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credentials

4. **Testing Framework** (high complexity)
   - Migrate from Test Kitchen to Molecule
   - Either convert InSpec tests to Ansible assertions or create integration

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Chef InSpec tests need to be preserved or converted to equivalent Ansible testing mechanisms
3. The Chef Automate and Chef Infra Server deployment should be replaced with equivalent Ansible automation
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for local development/testing
6. The security compliance requirements referenced in the InSpec tests must be maintained
7. No actual Chef cookbooks were found in the repository, only Chef InSpec tests and Chef Automate setup scripts
8. The repository appears to be primarily educational/demonstrative rather than production infrastructure code