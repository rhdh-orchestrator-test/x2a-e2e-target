# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef InSpec test profiles for compliance validation
2. Ansible playbooks for configuration management
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** as most of the configuration is already in Ansible format, with the main work being to convert the InSpec tests to Ansible-compatible testing frameworks and to replace the Chef server deployment scripts with Ansible playbooks.

**Estimated Timeline**: 2-3 weeks for a complete migration, with the following breakdown:
- 1 week: Convert InSpec tests to Ansible-compatible testing (Molecule/TestInfra)
- 1 week: Create Ansible roles for Chef server deployment
- 3-5 days: Documentation and knowledge transfer

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec profile for validating SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec profile for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS content verification, SSL protocol validation

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Molecule with TestInfra for infrastructure testing
  - Option 2: Use Ansible assert modules for basic validation
  - Option 3: Keep InSpec but integrate it with Ansible using the inspec_exec module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline integration
  - Compliance automation using OpenSCAP or Ansible Security Automation

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain:
  - Self-signed certificate generation
  - TLS 1.2 enforcement
  - Disabling of vulnerable protocols (SSL3)

- **SSH Hardening**: The InSpec tests validate SSH security configurations:
  - Root login restrictions
  - Migration should include equivalent Ansible tasks to enforce these settings

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks:
  - Challenge: Maintaining the same level of compliance validation
  - Mitigation: Use TestInfra with Molecule which has similar syntax and capabilities to InSpec

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible:
  - Challenge: Ensuring all Chef server configuration options are properly translated
  - Mitigation: Create dedicated Ansible roles for Chef server deployment or replace with AWX/Tower

- **Test Kitchen Integration**: Ensuring test continuity during migration:
  - Challenge: Maintaining testing workflow while transitioning
  - Mitigation: Gradually transition tests while maintaining both systems temporarily

### Migration Order

1. **website_https playbook** (already in Ansible format, low risk)
2. **poodle_fix playbook** (already in Ansible format, low risk)
3. **InSpec tests** (convert to TestInfra/Molecule, medium complexity)
4. **Chef server deployment scripts** (convert to Ansible roles, high complexity)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating these are examples for blog posts.
2. The Chef InSpec tests are used for validation of Ansible-deployed configurations, not as part of a larger Chef ecosystem.
3. The deployment scripts are standalone examples and not integrated with a larger Chef infrastructure.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.
5. There is no existing Ansible AWX/Tower infrastructure to integrate with.
6. The migration will maintain the same level of security validation currently provided by InSpec tests.
7. No external data sources or inventory systems need to be integrated.