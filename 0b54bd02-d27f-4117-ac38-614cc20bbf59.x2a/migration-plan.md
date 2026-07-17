# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks and Chef server deployment scripts to Ansible playbooks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment with Apache2, SSL/TLS compliance verification, self-signed certificate generation, virtual host configuration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server installation, user and organization creation, system configuration for Chef Automate

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec - needs to be replaced with Ansible-native testing framework configuration
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website with Apache2, including SSL certificate generation - can be preserved as-is
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities (specifically POODLE) by enforcing TLSv1.2 - can be preserved as-is
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website that verifies port 443 is listening, website returns 200 status code, and proper TLS protocols are enabled - needs conversion to Ansible-compatible test framework
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance that verifies root login is disabled - needs conversion to Ansible-compatible test framework
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate with hardcoded credentials - needs conversion to Ansible playbook
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server with hardcoded credentials - needs conversion to Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for compliance testing
  - Option 3: Continue using InSpec but integrate with Ansible using the ansible_inspec module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test framework

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (disabling SSLv3, enabling TLSv1.2) that must be preserved in the Ansible migration
  - Migration approach: Preserve the existing Ansible tasks in poodle_fix.yml that handle SSL configuration

- **SSH Security**: The repository includes SSH hardening tests (disabling root login)
  - Migration approach: Convert the InSpec SSH tests to equivalent Ansible tests while maintaining the same security checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: jtonello, password: password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbooks - this approach can be maintained but should use Ansible Vault for storing sensitive key material

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec, or maintain InSpec and integrate with Ansible

- **Maintaining Compliance Standards**: Ensuring that the compliance checks in the InSpec tests are fully preserved in the Ansible migration
  - Mitigation: Create a compliance mapping document to ensure all checks are preserved

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment that maintain the same functionality

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Preserve existing website_https.yml and poodle_fix.yml playbooks
2. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (Medium complexity): Convert Chef server deployment scripts to Ansible playbooks
4. **Test Kitchen Configuration** (Low complexity): Replace Test Kitchen with Ansible-native testing framework

### Assumptions

1. The primary goal is to move away from Chef while preserving the existing Ansible components
2. The InSpec tests need to be converted to an Ansible-compatible testing framework
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible playbooks for deploying alternative solutions
4. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be preserved as-is
5. The hardcoded credentials in the deployment scripts will be replaced with Ansible Vault
6. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
7. The compliance requirements expressed in the InSpec tests must be maintained in the Ansible migration