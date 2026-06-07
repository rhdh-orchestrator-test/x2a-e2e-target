# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks
2. Converting Chef InSpec tests to equivalent Ansible testing solutions
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Server**: Replace with Ansible Automation Platform or AWX (open-source version of Ansible Tower)
  - Provides similar functionality for centralized automation management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the Ansible configuration
  - Verify that only TLSv1.2 is enabled and SSLv3 is disabled

- **SSH Security**: Maintain the SSH root login restrictions validated by the InSpec test
  - Create an equivalent Ansible task to verify SSH configuration

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation
  - Challenge: InSpec provides specialized resources for testing that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible modules like `uri`, `command` with `assert`, and custom scripts where needed

- **Test Kitchen to Molecule**: Adapting the testing workflow
  - Challenge: Ensuring test environments are consistent between the old and new testing frameworks
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Challenge: Chef Automate provides specialized compliance reporting that needs an equivalent in the Ansible ecosystem
  - Mitigation: Implement Ansible Automation Platform with compliance add-ons or integrate with a third-party compliance tool

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **Testing Framework**: Convert from Test Kitchen to Molecule
3. **InSpec Tests**: Convert to Ansible-native testing solutions
4. **Chef Automate/Server Deployment**: Replace with Ansible Automation Platform deployment

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while maintaining the same level of compliance validation
2. The existing Ansible playbooks can be used with minimal modifications
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. Security compliance requirements (like STIG references in ssh_profile.rb) must be preserved in the new implementation
5. The deployment scripts for Chef Automate/Server are intended to be replaced with equivalent Ansible automation
6. No external data sources or integrations beyond what's visible in the repository are required
7. The migration does not need to address scaling concerns as the current implementation appears to be for demonstration purposes