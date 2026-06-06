# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use community.general.assert module for basic validation
  - Option 3: Implement Ansible roles with built-in testing

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule provides similar functionality for testing Ansible roles with different drivers and verifiers

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain compliance with security standards referenced in InSpec tests

- **SSH Hardening**: Preserve the SSH security controls verified by the InSpec tests
  - Ensure root login remains disabled
  - Maintain compliance with STIG requirements referenced in the tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec provides specialized resources for testing that may not have direct equivalents in Ansible
  - Mitigation: Use Molecule with Testinfra or implement custom Ansible assertion tasks

- **Chef Automate/Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The scripts install Chef-specific components that need equivalent functionality in Ansible
  - Mitigation: Research alternatives like AWX/Tower for centralized management or implement custom Ansible roles

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, requires conversion to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete rewrite as Ansible playbooks

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes
2. The InSpec tests are currently used for validation and compliance checking, and this functionality needs to be preserved
3. The deployment scripts are used for setting up Chef infrastructure, which may need to be replaced with equivalent Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations not visible in the provided files
6. The migration is primarily focused on replacing Chef InSpec with Ansible-native testing while preserving existing Ansible playbooks
7. No specific performance requirements or scaling considerations are mentioned in the source files