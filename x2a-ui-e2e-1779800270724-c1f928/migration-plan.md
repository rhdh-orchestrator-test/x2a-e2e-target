# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and verify secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML content for the web server. Can be preserved as-is or converted to an Ansible template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Test for native Ansible testing capabilities
  - Option 3: Continue using InSpec but invoke it from Ansible rather than Chef

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Custom Ansible playbook for test environment provisioning

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise Ansible management
  - Option 2: Custom Ansible playbooks for configuration management without a central server

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Convert the existing Ansible playbook (poodle_fix.yml) to an Ansible role with proper documentation

- **SSH Security**: The SSH security profile tests must be preserved
  - Approach: Convert the InSpec SSH tests to equivalent Ansible assertions or Testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to an Ansible-compatible testing framework
  - Mitigation: Use Testinfra which has similar syntax and capabilities to InSpec

- **Compliance Reporting**: InSpec provides compliance reporting that may need to be replicated
  - Mitigation: Consider using Ansible Tower/AWX with compliance plugins or integrate with a dedicated compliance tool

- **Test Kitchen Replacement**: Finding an equivalent to Test Kitchen's workflow
  - Mitigation: Molecule provides similar functionality for Ansible roles and can use various drivers including Vagrant

### Migration Order

1. Convert InSpec tests to Ansible-compatible tests (low risk, preserves verification capability)
2. Replace Test Kitchen with Molecule (moderate complexity)
3. Create Ansible roles from existing playbooks (low complexity, mostly reorganization)
4. Replace Chef Automate/Infra Server deployment scripts with Ansible equivalents (moderate complexity)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes
2. The security compliance requirements represented in the InSpec tests must be preserved in the Ansible solution
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent functionality
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The repository appears to be primarily for demonstration/educational purposes rather than production use
7. The hardcoded credentials in the deployment scripts are not used in production environments