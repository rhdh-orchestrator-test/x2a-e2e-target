# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing configuration.
- `index.html`: Sample HTML file used for testing the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for integration testing
  - Option 3: Ansible Lint for static code analysis
  - Option 4: Consider Ansible's assert module for runtime validation

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: The deployment scripts should be converted to Ansible playbooks that can install and configure equivalent monitoring and compliance solutions:
  - Consider Ansible AWX/Tower as a replacement for Chef Automate
  - Consider using Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older SSL/TLS protocols
  
- **SSH Security**: The SSH root login compliance check must be preserved:
  - Convert the InSpec control to an Ansible task that verifies the same configuration
  - Consider implementing as an Ansible pre-task or separate compliance playbook

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - These should be moved to Ansible Vault during migration

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the InSpec resource models (port, http, ssl, sshd_config)
  - Creating equivalent checks using Ansible modules
  - Preserving the compliance metadata (STIG IDs, CCI references)

- **Compliance Reporting**: Chef InSpec provides structured compliance reporting:
  - Need to identify an Ansible-compatible solution for compliance reporting
  - Consider integrating with tools like Ansible Tower/AWX for reporting

- **Test Kitchen Replacement**: Test Kitchen provides a structured testing workflow:
  - Molecule will need to be configured to provide similar capabilities
  - May require additional setup for multi-platform testing

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes.
   
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-native testing solutions.
   
3. **Chef Automate/Server Deployment Scripts**: Convert these bash scripts to Ansible playbooks.
   
4. **Test Kitchen Configuration**: Replace with Molecule or other Ansible testing framework.

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes.

3. The target environment will continue to be Ubuntu 20.04 or compatible systems.

4. The deployment scripts for Chef Automate/Server are intended to be replaced with equivalent functionality using Ansible-native tools.

5. No specific performance requirements are mentioned for the migration.

6. The security compliance requirements (STIG, CCI references) must be preserved in the new implementation.

7. The migration will not change the fundamental architecture or functionality of the applications being configured.