# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks, along with Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible equivalents

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the repository primarily contains Ansible playbooks already with Chef InSpec tests and Chef deployment scripts.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file for testing web server functionality - can be preserved as-is

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Server**: Replace with Ansible AWX/Tower or other Ansible-compatible CI/CD solutions

### Security Considerations

- **SSL Configuration**: The existing playbooks already implement security best practices for SSL/TLS:
  - Disabling SSLv3 (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - These configurations should be preserved in the migrated solution

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Root login disabled
  - These tests should be converted to Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with appropriate conditionals or integrate with Molecule for testing

- **Chef Server Replacement**: Determining the appropriate Ansible management platform:
  - Challenge: Chef Automate/Server provides specific functionality for configuration management
  - Mitigation: Evaluate Ansible AWX/Tower as replacement or determine if this functionality is still needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity, requires conversion to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions about management platform

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible integration, not for production deployment
2. The Chef Automate/Server deployment scripts are for demonstration purposes and may not need direct replacement if the focus is on Ansible
3. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes
4. Test Kitchen is used primarily for testing and can be replaced with Ansible-native testing tools
5. No external dependencies or modules are referenced beyond what's visible in the repository
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. No complex state management or data persistence requirements exist
8. No custom Chef resources or complex Chef-specific functionality is being used