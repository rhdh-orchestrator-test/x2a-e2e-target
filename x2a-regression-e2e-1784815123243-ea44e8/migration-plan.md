# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily focused on examples and demonstrations rather than production infrastructure code. It contains:

1. Ansible playbooks with Chef InSpec testing integration
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and shell scripts to convert. The estimated timeline for migration would be 1-2 days of work for a skilled Ansible developer.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but call it from Ansible using the `command` module

- **Test Kitchen with Vagrant**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant setup with direct Ansible provisioning

- **Chef Automate/Server Deployment**: Replace with:
  - Ansible roles for configuration management without requiring Chef infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should:
  - Maintain the TLS 1.2 requirement (disabling older protocols)
  - Consider updating to also allow TLS 1.3 for better security
  - Use Ansible Vault for storing certificate information

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Include equivalent Ansible tasks to enforce SSH security settings
  - Maintain compliance with the security requirements in the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec Testing Integration**: The current setup uses InSpec for compliance testing. Challenge will be:
  - Finding equivalent Ansible-native testing capabilities
  - Ensuring the same level of compliance verification
  - Mitigation: Consider using Ansible's assert module or maintaining InSpec as a separate tool called from Ansible

- **Chef Server Deployment**: The current scripts deploy Chef Server infrastructure. Challenge will be:
  - Determining if Chef Server is still needed in the new architecture
  - If needed, creating equivalent Ansible roles for Chef Server deployment
  - Mitigation: Evaluate if the Chef infrastructure can be completely replaced by Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need testing framework updates
2. **Testing Framework**: Replace Test Kitchen with Molecule or equivalent
3. **Chef Deployment Scripts**: Convert to Ansible roles if Chef infrastructure is still required

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production infrastructure
2. The InSpec tests are essential for compliance verification and need equivalent functionality in the migrated solution
3. The Chef Server deployment scripts may not be needed if moving to a pure Ansible solution
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The hardcoded credentials in the scripts are for demonstration only and will be properly secured in the migrated solution