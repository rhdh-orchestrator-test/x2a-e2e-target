# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation, along with Chef server deployment scripts. The migration scope is relatively small, focusing on:

1. Chef InSpec tests that need to be migrated to Ansible-compatible testing frameworks
2. Ansible playbooks that may need to be updated or standardized
3. Chef server deployment scripts that need to be converted to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and InSpec tests for demonstrating compliance automation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Infra Server and Chef Automate
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2.
- `chef-and-ansible/index.html`: Static HTML content for the web server. No migration needed, can be used as-is in Ansible templates.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH security configuration.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper documentation
  
- **SSH Security**: The SSH security checks in ssh_profile.rb need to be preserved
  - Approach: Convert InSpec tests to Ansible assert statements or Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage
  - Count: 2 credential sets identified in setup-automate scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Molecule's verifier plugins or custom Ansible tasks with assert module
  
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same setup steps as the bash scripts

### Migration Order

1. **chef-and-ansible** Ansible playbooks (low risk, already in Ansible format)
   - Review and update website_https.yml to current Ansible best practices
   - Review and update poodle_fix.yml to current Ansible best practices
   - Add proper documentation
   
2. **chef-and-ansible** InSpec tests (moderate complexity)
   - Convert tests/website_https_verify.rb to Ansible-native testing mechanisms
   - Convert tests/ssh_profile.rb to Ansible-native testing mechanisms
   - Ensure all security checks are preserved

3. **setup-automate** scripts (high complexity)
   - Convert deploy-automate.sh to Ansible roles
   - Convert deploy-chef-server.sh to Ansible roles
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. The InSpec tests are critical for compliance validation and must be preserved in functionality
3. The deployment scripts for Chef server will be replaced with Ansible playbooks that deploy alternative infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements specified in the InSpec tests must be maintained
6. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
7. The Test Kitchen setup is primarily for development/testing and not production deployment