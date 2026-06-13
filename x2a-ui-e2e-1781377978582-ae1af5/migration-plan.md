# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used for compliance automation alongside Ansible deployments. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-native testing solutions
2. Preserving the existing Ansible playbooks with minimal changes
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that most of the infrastructure code is already in Ansible format, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
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
  - Option 1: Migrate to Ansible Molecule for testing infrastructure
  - Option 2: Use ansible-test framework
  - Option 3: Implement tests using Python's pytest with testinfra plugin

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with Ansible verifier instead of InSpec

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for configuration management
  - Consider migrating to AWX/Ansible Tower for web UI and control

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Maintain the same configuration parameters in the Ansible playbooks

- **SSH Security Controls**: The SSH security validation must be preserved
  - Approach: Convert InSpec SSH controls to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - website_https module: 0 hardcoded credentials
    - poodle_fix module: 0 hardcoded credentials
    - chef-automate-deploy module: 3 credentials (username, password, email)
    - chef-server-deploy module: 3 credentials (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Consider implementing custom reporting using Ansible callbacks or integrating with tools like AWX/Tower

- **SSL Testing**: The SSL protocol validation in InSpec is concise and readable
  - Mitigation: Create a custom Ansible module or use shell commands with assert to validate SSL configurations

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to replace with Ansible roles

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't require functional changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Test Kitchen can be replaced or reconfigured to work with Ansible-native testing
5. The security compliance requirements represented in the InSpec tests must be preserved
6. The deployment scripts for Chef Automate/Server will be replaced with equivalent Ansible automation
7. No external integrations or dependencies beyond what's visible in the repository need to be considered