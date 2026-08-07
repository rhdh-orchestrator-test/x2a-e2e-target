# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to medium complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **InSpec Tests**: Convert to Ansible-native testing with:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - molecule for scenario-based testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the SSL protocol settings are preserved in the migrated Ansible roles
  
- **SSH Hardening**: The InSpec tests check for SSH root login restrictions
  - Approach: Implement equivalent SSH hardening in Ansible and maintain testing

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
    - Migration approach: Move to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use testinfra which has similar syntax and capabilities to InSpec
  
- **Chef Automate/Server Deployment**: Converting bash scripts to Ansible roles
  - Mitigation: Create dedicated Ansible roles for Chef server deployment with proper idempotence checks

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Convert to Ansible role structure with proper variable management
   - Implement equivalent tests using testinfra

2. **poodle_fix.yml** (low risk, already Ansible)
   - Convert to Ansible role or include in the website role
   - Ensure security hardening is maintained

3. **InSpec Tests** (medium complexity)
   - Convert to testinfra or other Ansible-compatible testing framework
   - Ensure all security checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible roles
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks are functional and tested
2. The InSpec tests are currently used for compliance validation
3. The repository is primarily used for demonstration/example purposes rather than production
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or similar
6. The deployment scripts are intended for on-premises or generic cloud VMs
7. No complex orchestration or integration with external systems is required