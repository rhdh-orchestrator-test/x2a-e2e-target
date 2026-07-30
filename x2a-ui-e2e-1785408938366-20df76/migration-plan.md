# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary focus will be on:
1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the Chef Automate/Infra Server deployment scripts are replaced with Ansible playbooks
3. Maintaining the compliance testing capabilities while fully migrating to Ansible

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration testing, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTPS verification, SSL protocol verification

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for testing web server configuration
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing, consider using OpenSCAP with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Molecule can handle the provisioning, converge, verify workflow that Test Kitchen provides

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create roles and playbooks to handle the installation and configuration
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate's dashboard functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the Ansible migration maintains:
  - Proper TLS protocol settings (TLS 1.2 enabled, older protocols disabled)
  - Self-signed certificate generation (consider using Ansible's crypto modules)

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure:
  - SSH hardening is maintained in the Ansible playbooks
  - Testing for SSH configuration is implemented in the new testing framework

- **Credentials Management**: The Chef server deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Remove hardcoded passwords from scripts (found in deploy-automate.sh and deploy-chef-server.sh)
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 3 credentials (username, password, email)
    - chef-server-deployment: 3 credentials (username, password, email)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to an Ansible-compatible testing framework:
  - InSpec has a specific syntax and testing approach that needs to be mapped to Ansible testing tools
  - Mitigation: Use Ansible Molecule with testinfra or GOSS for similar testing capabilities

- **Maintaining Compliance Automation**: Ensuring the compliance testing capabilities are preserved:
  - Chef InSpec is specifically designed for compliance testing
  - Mitigation: Consider using OpenSCAP with Ansible, or maintaining InSpec as a standalone tool called from Ansible

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible:
  - The scripts perform specific Chef server configuration tasks
  - Mitigation: Create dedicated Ansible roles for Chef server deployment if still needed, or replace with AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need minor adjustments for best practices and integration with the new testing framework.

2. **Testing Framework**: Migrate the InSpec tests to Ansible Molecule or another compatible testing framework:
   - ssh_profile.rb
   - website_https_verify.rb

3. **Deployment Scripts**: Convert the bash deployment scripts to Ansible playbooks:
   - deploy-automate.sh
   - deploy-chef-server.sh

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can work alongside Ansible.
2. The actual infrastructure being managed is relatively simple (web servers with HTTPS).
3. There's no complex Chef cookbook structure that needs migration.
4. The deployment scripts for Chef Automate/Infra Server are used for setting up testing environments rather than production systems.
5. The organization wants to fully migrate to Ansible and not maintain a hybrid Chef/Ansible environment.
6. The compliance testing capabilities provided by InSpec are important to maintain in the Ansible migration.
7. The Test Kitchen configuration is used primarily for testing and demonstration, not for production deployments.