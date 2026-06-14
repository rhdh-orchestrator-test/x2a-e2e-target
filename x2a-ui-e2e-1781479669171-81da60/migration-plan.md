# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with a focus on:

1. Migrating InSpec tests to Ansible-compatible testing frameworks
2. Ensuring existing Ansible playbooks follow best practices
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

Given the limited scope and complexity, this migration could be completed in approximately 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used for testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices enforcement

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set system parameters (hostname, sysctl values)
  - Install and configure alternative compliance and infrastructure management tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in the Ansible configuration
  - Ensure root login remains disabled
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use secure key management

### Technical Challenges

- **Compliance Testing Framework**: InSpec provides specific security and compliance testing capabilities that need equivalent functionality in Ansible
  - Mitigation: Evaluate ansible-test, Molecule, or other testing frameworks that can provide similar compliance validation

- **Test Coverage**: Ensuring the same level of test coverage when migrating from InSpec to Ansible-native testing
  - Mitigation: Create a test coverage matrix to ensure all current tests have equivalent implementations

- **Deployment Automation**: The Chef Automate/Infra Server deployment scripts contain specific configuration steps that need to be replicated
  - Mitigation: Research alternative infrastructure management tools that can be deployed via Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, focus on best practices and optimization
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires converting Ruby-based tests to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific tooling with Ansible alternatives

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functional but may need optimization for best practices
3. A replacement for Chef Automate's compliance and infrastructure management capabilities is needed
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The security requirements specified in the InSpec tests must be maintained in the migrated solution
6. No specific Ansible version requirements have been identified
7. The migration will not change the fundamental architecture or functionality of the applications