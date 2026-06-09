# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef server CLI tools
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Test for native Ansible testing capabilities
  - Option 3: Continue using InSpec but integrate with Ansible workflows

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible automation platform (AAP) or other Ansible management solutions

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Ensure the same SSL protocol restrictions are maintained in the migrated Ansible roles

- **SSH Security Controls**: The SSH root login compliance check needs to be preserved
  - Approach: Convert the InSpec control to an equivalent Ansible assertion or Molecule test

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Use Ansible's crypto modules to maintain the same certificate generation functionality

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-compatible tests
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities to InSpec

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that install and configure Chef server components or replace with Ansible Automation Platform

- **Test Kitchen Integration**: Replacing Test Kitchen workflow with Ansible-native testing
  - Mitigation: Adopt Molecule as the testing framework for Ansible roles and playbooks

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, just need to be reorganized into proper Ansible roles
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, convert to Molecule/Testinfra tests
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, convert to Ansible roles or replace functionality

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md
2. The Chef InSpec tests are used for validation only and not for remediation
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production
4. The target environment is Ubuntu 20.04 as specified in kitchen.yml
5. The Apache version (2.4.41-4ubuntu3.10) specified in the playbook is required for compatibility reasons
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
7. The SSH compliance check is based on STIG requirements and needs to be preserved in the migration