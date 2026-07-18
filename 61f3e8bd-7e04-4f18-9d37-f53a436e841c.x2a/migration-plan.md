# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for web server configuration and security compliance. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **inspec-tests**:
    - Description: Chef InSpec tests for HTTPS website verification and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH root login security check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for HTTPS website deployment
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL POODLE vulnerability remediation
- `chef-and-ansible/index.html`: Sample HTML file used in website deployment
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible using the command module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collections testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml
  - Approach: Use Ansible's lineinfile or template module to enforce TLSv1.2 protocol
  
- **SSH Security**: Maintain SSH root login restrictions from InSpec tests
  - Approach: Create Ansible task to configure sshd_config with appropriate settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates generated during playbook execution
  - Approach: Replace with Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions
  - Mitigation: Use Ansible assert module with appropriate conditionals or maintain InSpec as a verification tool

- **Chef Server Deployment**: Replacing Chef server deployment scripts
  - Mitigation: Create Ansible roles for configuration management server deployment if needed, or eliminate if moving fully to Ansible

### Migration Order

1. **chef-and-ansible/website_https.yml** (already in Ansible format, minimal changes needed)
2. **chef-and-ansible/poodle_fix.yml** (already in Ansible format, minimal changes needed)
3. **chef-and-ansible/tests** (convert InSpec tests to Ansible assertions or maintain as separate verification)
4. **setup-automate** (lowest priority, replace with Ansible roles if needed)

### Assumptions

1. The primary purpose of this repository is demonstration/examples rather than production code
2. The InSpec tests are used for verification of infrastructure rather than as part of a larger compliance framework
3. The Chef server deployment scripts are examples and not part of the core functionality
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external data sources or complex state management is required
6. No complex orchestration or coordination with external systems is needed