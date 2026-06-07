# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

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
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts mention they can be used on "on-prem or cloud VM"

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the community.general.test_connection module for network validation

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained during migration
  - Consider updating to include more recent TLS versions (TLSv1.3) if target systems support it

- **SSH Hardening**: The SSH root login check must be preserved
  - Convert the InSpec control to an Ansible assert or use ansible-lint security checks

- **Credentials in Scripts**: The deployment scripts contain hardcoded credentials
  - Replace with Ansible Vault for secure credential storage
  - Identified credentials:
    - Username: jtonello
    - Password: password (plaintext in scripts)
    - Email: jtonello@chef.lab

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the detailed InSpec tests to equivalent Ansible validation
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use a combination of Ansible modules like uri, command, and assert to replicate functionality

- **SSL Certificate Validation**: Ensuring proper validation of SSL certificates
  - Challenge: InSpec has built-in SSL validation capabilities
  - Mitigation: Use the uri module with validate_certs parameter and custom validation logic

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - These are already in Ansible format and require minimal changes
   - Update to use more modern Ansible practices if needed

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Convert to Ansible playbooks
   - Implement Ansible Vault for credential storage

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible-native testing solutions
   - Integrate with CI/CD pipeline for automated validation

### Assumptions

1. The existing Ansible playbooks are compatible with current Ansible versions and don't require significant updates
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The security requirements (TLS 1.2, SSH hardening) remain the same
4. The Chef Automate and Chef Server deployment will be replaced with equivalent functionality, not necessarily identical components
5. Test Kitchen integration is required for the migrated solution
6. The migration does not need to preserve Chef InSpec as a testing tool
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives