# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef InSpec profiles for compliance testing
2. Ansible playbooks for configuration management
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on converting InSpec tests to Ansible testing frameworks while preserving the existing Ansible playbooks and replacing the Chef server deployment scripts with Ansible equivalents.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file for testing infrastructure code
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu (inferred from apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Not specified, appears to be generic VM deployment
- **Cloud Platform**: Not specified, appears to be cloud-agnostic with potential for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-test framework

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and API
  - Option 2: Use Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper documentation
  
- **SSH Hardening**: The SSH security checks must be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Create custom Ansible modules or use assert with well-defined error messages
  
- **Chef Server Functionality**: Replacing Chef Server's organization and user management
  - Mitigation: Use AWX/Tower's RBAC features or integrate with external identity providers

- **Compliance Reporting**: Replacing Chef InSpec's compliance reporting capabilities
  - Mitigation: Integrate with Ansible Automation Platform's compliance features or use a third-party compliance tool

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Convert to roles for better organization
   
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure equivalent coverage and reporting

3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to replace Chef server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require functional changes
2. The InSpec tests are currently used for validation and compliance reporting
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced with Ansible infrastructure
4. No external Chef cookbooks or recipes are being used beyond what's visible in the repository
5. The target environment will support Ansible's requirements (Python, SSH access)
6. The migration will maintain the same level of security compliance currently provided by InSpec tests