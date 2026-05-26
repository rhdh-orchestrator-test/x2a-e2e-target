# MIGRATION FROM CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration, including port listening status, HTTP response, and SSL/TLS protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response validation, SSL/TLS protocol security checks

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration, specifically checking that root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks, CCI compliance mapping

- **website_https_deployment**:
    - Description: Ansible playbook for deploying an HTTPS website with Apache2, including SSL certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - should be migrated to Ansible-native testing framework
- `index.html`: Static HTML file for website deployment - can be preserved as-is or converted to an Ansible template

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSH Security Compliance**: Migrate the SSH compliance checks to Ansible-native security checks
  - Consider using ansible-lint security rules
  - Implement equivalent checks using Ansible assert tasks

- **SSL/TLS Security**: Preserve the SSL/TLS hardening in the Ansible playbooks
  - Ensure the POODLE fix remains implemented
  - Consider adding additional TLS hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates and keys should be managed securely, potentially using ansible-vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible testing constructs
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider implementing custom reporting using Ansible callback plugins or integrating with compliance tools like OpenSCAP

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be completely rewritten as Ansible roles
  - Mitigation: Create dedicated Ansible roles for infrastructure components previously managed by Chef

### Migration Order

1. Convert InSpec tests to Ansible-native testing (low risk, foundational)
   - website_https_verify.rb → Molecule/Testinfra tests
   - ssh_profile.rb → Ansible security tasks with assert statements

2. Migrate Test Kitchen to Molecule (moderate complexity)
   - kitchen.yml → molecule.yml and associated configuration

3. Convert Chef Automate deployment scripts to Ansible roles (high complexity)
   - deploy-automate.sh → ansible-role-automate
   - deploy-chef-server.sh → ansible-role-chef-server

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) will be preserved with minimal changes
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for local development and testing
4. The Chef Automate and Chef Server components are intended to be replaced with equivalent functionality in Ansible
5. No additional Chef cookbooks or recipes exist beyond what's visible in the repository
6. The InSpec tests are currently being used for post-deployment validation rather than continuous compliance monitoring
7. No external dependencies or integrations exist beyond what's explicitly defined in the repository files