# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible compliance checks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules and blocks
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Ansible Automation Platform's compliance capabilities

- **Test Kitchen**: Replace with:
  - Option 1: molecule for Ansible role testing
  - Option 2: ansible-test for collection testing

- **Vagrant**: Can be retained as is or replaced with:
  - Option 1: Continue using Vagrant with Ansible provisioner
  - Option 2: Use molecule with docker or podman driver for lighter testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the SSL protocol restrictions are maintained in the migrated solution

- **SSH Security**: The SSH root login compliance check must be preserved
  - Approach: Convert the InSpec control to an Ansible task that checks the same configuration

- **Credentials Management**: 
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in each deployment script

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules or consider integrating with tools like ansible-lint or AAP compliance

- **Chef Automate Replacement**: Determining the appropriate Ansible alternative for Chef Automate functionality
  - Mitigation: Consider Ansible Automation Platform as a replacement for Chef Automate's functionality

- **Test Kitchen Replacement**: Finding an equivalent testing framework for Ansible
  - Mitigation: Adopt molecule as the testing framework for Ansible roles and playbooks

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing approaches
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks with proper variable management

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The InSpec tests are currently being used for validation and compliance checking, and this functionality needs to be preserved
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The migration will maintain the same level of security compliance as the original implementation
6. No external dependencies or integrations beyond what's visible in the repository need to be considered