# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Maintain InSpec for compliance testing or migrate to Ansible-native solutions:
  - Option 1: Keep InSpec tests and integrate with Ansible using the `inspec` Ansible module
  - Option 2: Replace InSpec tests with equivalent Ansible assertions or Molecule verifiers

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols
  - Migration approach: Preserve the security hardening in the new Ansible roles
  - Consider updating to include TLS 1.3 support

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining the compliance testing capabilities while migrating to a pure Ansible solution
  - Mitigation: Use Ansible's `inspec` module or migrate to Molecule with testinfra for testing

- **Chef Automate/Server Deployment**: Converting bash scripts to Ansible roles
  - Mitigation: Create dedicated Ansible roles for Chef server deployment with proper idempotence checks

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Add documentation and improve variable naming

2. **poodle_fix playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Consider merging with the website_https role as an optional security enhancement

3. **InSpec tests** (moderate complexity)
   - Either maintain as-is and integrate with Ansible using the inspec module
   - Or convert to equivalent Molecule tests

4. **Chef deployment scripts** (high complexity)
   - Convert bash scripts to Ansible roles for Chef server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to maintain the same functionality while improving the structure and maintainability of the Ansible code.
2. Chef InSpec will continue to be used for compliance testing, as it appears to be a key component of the repository's purpose.
3. The bash scripts for Chef Automate/Server deployment are intended to be converted to Ansible roles rather than maintained as bash scripts.
4. The target environment will remain Ubuntu 20.04 or later.
5. Vagrant will continue to be used for local development and testing.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.
7. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with proper secret management.