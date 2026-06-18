# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Molecule with Testinfra for infrastructure testing
  - **Option 2**: Ansible Molecule with Goss for infrastructure testing
  - **Option 3**: Ansible Test Plugins for basic validation

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and control
  - Ansible Collections for configuration management
  - Compliance scanning can be handled by OpenSCAP integration with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Convert the InSpec tests to equivalent Ansible assertions or Molecule tests to verify SSL/TLS security

- **SSH Security**: The SSH security checks in ssh_profile.rb need to be preserved
  - Approach: Convert to Ansible security roles or OpenSCAP checks

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using Ansible Vault or external certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the detailed InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Molecule with Testinfra or Goss which provide similar testing capabilities

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Integrate with OpenSCAP or AWX/Tower compliance features

- **Chef Server Deployment**: Converting the Chef server deployment scripts to idempotent Ansible playbooks
  - Mitigation: Use Ansible roles for Chef server deployment or replace with AWX/Tower deployment

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks or replace functionality with Ansible AWX/Tower

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality
3. The security and compliance testing capabilities of InSpec need to be preserved in the Ansible ecosystem
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. No specific cloud provider is targeted, but the solution should work in cloud environments
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure credential management
7. The Test Kitchen configuration will be replaced with Ansible Molecule for testing
8. The existing Ansible playbooks follow best practices and don't require significant refactoring