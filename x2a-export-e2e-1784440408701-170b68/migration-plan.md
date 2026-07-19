# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing integration

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on:
- Converting Chef deployment scripts to Ansible playbooks
- Preserving the InSpec testing functionality within an Ansible-only workflow
- Ensuring security configurations are properly maintained

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec integration for deploying and testing a secure HTTPS website
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS configuration. Migration considerations include preserving SSL certificate generation and virtual host configuration.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring security hardening is maintained.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing solutions or adapting to use Molecule.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality. Migration considerations include converting to Ansible testing framework or maintaining InSpec integration.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible testing framework or maintaining InSpec integration.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure deployment.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing or maintain InSpec integration
  - Option 1: Use Ansible's built-in assert module and uri module for basic testing
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Maintain InSpec integration for compliance testing (recommended for complex compliance requirements)

- **Test Kitchen (latest)**: Replace with Ansible-native testing framework
  - Replace with Molecule for Ansible role testing

- **Vagrant (latest)**: Can be maintained as the development environment

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create Ansible roles for infrastructure deployment that were previously handled by Chef

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the current configuration
  - Ensure TLSv1.2 enforcement is preserved (from poodle_fix.yml)
  - Maintain proper SSL certificate generation and configuration

- **SSH Security Hardening**: Maintain the SSH security controls tested by the InSpec profile
  - Ensure root login remains disabled
  - Preserve compliance with security requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should use Ansible Vault or external secret management
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec Integration**: Maintaining compliance testing capabilities while migrating to Ansible-only workflow
  - Mitigation: Use Ansible's built-in modules for basic testing and consider maintaining InSpec for complex compliance requirements or migrate to Ansible-native compliance solutions

- **SSL Certificate Management**: Ensuring proper handling of SSL certificates in the migrated solution
  - Mitigation: Use Ansible's openssl_* modules as already demonstrated in the existing playbooks

- **User and Organization Management**: Replacing Chef user and organization creation with Ansible equivalents
  - Mitigation: Create custom Ansible roles to manage users and organizations for the target infrastructure

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, already in Ansible format)
   - Minimal changes needed as these are already Ansible playbooks
   - Focus on improving the playbooks with Ansible best practices
   - Update testing framework from Test Kitchen to Molecule

2. **InSpec Tests** (moderate complexity)
   - Decide whether to maintain InSpec integration or migrate to Ansible-native testing
   - If maintaining InSpec, update integration with Ansible workflow
   - If migrating, create equivalent tests using Ansible modules

3. **Chef Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management for credentials
   - Create roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible, not to provide production-ready infrastructure code.

2. The Chef deployment scripts are used for setting up test environments, not production systems.

3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.

4. The target environment for the migrated solution will continue to be Ubuntu 20.04 or compatible systems.

5. The migration will maintain the same level of security hardening and compliance testing as the original implementation.

6. The InSpec tests are considered valuable and should be preserved in some form, either through continued InSpec integration or equivalent Ansible testing.

7. The repository is primarily used for demonstration and learning purposes rather than managing actual production infrastructure.