# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure a web server with HTTPS support and security hardening
2. Chef InSpec tests used for compliance validation of the Ansible-managed infrastructure
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure management into Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration and security
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom modules for compliance testing
  - Option 2: Maintain InSpec as a standalone testing tool but invoke it from Ansible
  - Option 3: Migrate to Molecule for testing Ansible roles with testinfra for verification

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule for Ansible role testing
  - Option 2: Create custom Ansible playbooks for test environment provisioning

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Create an Ansible role for Apache that includes the same SSL hardening parameters

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that applies the same security controls

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - Plain text passwords are used in the Chef server deployment scripts (userpassword='password')
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible verification mechanisms
  - Mitigation strategy: Use ansible.builtin.assert or custom modules to perform similar validation checks

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible automation
  - Mitigation strategy: Create Ansible roles to deploy alternative configuration management or compliance tools if needed

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure with variables

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate into the website-https role as a security hardening task
   - Ensure idempotency and proper testing

3. **InSpec tests** (moderate complexity)
   - Convert to equivalent Ansible verification mechanisms
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Determine if Chef Automate/Server is still needed
   - If yes: Create Ansible roles to deploy and configure Chef components
   - If no: Replace with pure Ansible solution for configuration management and compliance

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation
2. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be central to the actual infrastructure
3. The target environment is Ubuntu 20.04, but the solution should be adaptable to other Linux distributions
4. The security hardening focuses on web server HTTPS configuration and SSH settings
5. No complex application deployment or database configuration is involved
6. The migration will consolidate to pure Ansible while maintaining or improving the compliance testing capabilities