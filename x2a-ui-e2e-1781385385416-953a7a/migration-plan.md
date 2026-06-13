# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a small number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module with appropriate checks
  - Option 2: Integrate with Molecule for testing
  - Option 3: Use the community.general.test_connection module for basic connectivity tests

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are correctly migrated
  - Maintain the same security posture by disabling SSLv3 and only enabling TLSv1.2

- **SSH Security**: The SSH root login check must be preserved in the Ansible testing framework
  - Convert the InSpec control to an equivalent Ansible assertion or Molecule verification

- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials
  - In the Ansible migration, use Ansible Vault to secure these credentials
  - Identified credentials:
    - Username: jtonello
    - Password: password (plaintext in both deployment scripts)
    - Email: jtonello@chef.lab

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the InSpec tests to Ansible-native testing will require careful mapping of assertions
  - Challenge: InSpec has specific matchers for SSL/TLS protocols that may not have direct equivalents in Ansible
  - Mitigation: May need to use shell commands with assert or custom modules

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Challenge: The scripts use Chef-specific CLI tools that need Ansible equivalents
  - Mitigation: Research Ansible modules for Chef management or use the command module with appropriate idempotency checks

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and only need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity to convert to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to convert to Ansible playbooks

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The security requirements specified in the InSpec tests must be maintained in the Ansible migration
4. The Chef Automate and Chef Server deployment is still needed in the migrated solution
5. The repository is primarily used for demonstration/example purposes rather than production deployment
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives in the migration