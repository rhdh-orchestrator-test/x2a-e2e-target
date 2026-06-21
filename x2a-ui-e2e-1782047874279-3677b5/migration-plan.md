# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec test profiles for compliance validation
2. Chef Automate/Chef Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-compatible testing frameworks and converting Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, depending on familiarity with Ansible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for validating HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, CCI compliance mapping, STIG validation

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
  - Migration considerations: Replace with Ansible-native testing framework like Molecule
  
- `website_https.yml`: Ansible playbook for configuring HTTPS on a web server
  - Migration considerations: Already in Ansible format, can be used as-is or refactored into roles
  
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
  - Migration considerations: Already in Ansible format, can be used as-is or refactored into roles

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with one of the following Ansible-compatible testing frameworks:
  - **Ansible Lint**: For static code analysis of Ansible playbooks
  - **Molecule**: For comprehensive Ansible role testing
  - **testinfra**: Python-based testing framework that can be used with Ansible
  - **ansible-test**: Built-in Ansible testing tool

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSH Security Controls**: The SSH compliance profile needs to be converted to Ansible security checks
  - Migration approach: Convert InSpec controls to Ansible pre/post tasks that validate the same security requirements
  
- **SSL/TLS Configuration**: The HTTPS verification tests need equivalent Ansible validation
  - Migration approach: Use Ansible URI module or testinfra for HTTP/HTTPS validation

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Mapping**: The InSpec tests include compliance mappings (CCI, STIG) that need to be preserved
  - Mitigation: Document compliance mappings in Ansible role metadata or use Ansible tags to maintain traceability

- **Test Result Reporting**: InSpec provides structured test results that need equivalent reporting in Ansible
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with tools like AWX/Tower for reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, review and refactor into roles if needed
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles/playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The hardcoded credentials in deployment scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 as specified in kitchen.yml
4. Vagrant is the preferred local testing platform
5. The deployment scripts are designed for single-node Chef Server/Automate installations
6. There's no existing Ansible inventory or group_vars/host_vars structure to integrate with
7. The migration will maintain the same level of compliance validation currently provided by InSpec
8. No external data sources or integrations beyond what's visible in the repository