# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles with appropriate checks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is more Ansible-native

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions from the InSpec test
  - Convert the InSpec control to an Ansible task that enforces the same policy

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 1 password (userpassword variable)
    - chef-server-deployment: 1 password (userpassword variable)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module or integrate with tools like Molecule

- **Chef Automate/Server Deployment**: Replacing Chef Automate and Chef Infra Server deployment scripts
  - Mitigation: Create Ansible roles for deploying alternative compliance and configuration management solutions

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec tests (website_https_verify.rb, ssh_profile.rb) - Medium complexity, requires conversion to Ansible testing
3. Chef deployment scripts (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without Chef dependencies
2. The InSpec tests are used for compliance validation and need to be replaced with equivalent Ansible functionality
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with Ansible roles for an alternative solution
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant
5. The security requirements (SSL configuration, SSH hardening) must be maintained in the migrated solution
6. The repository appears to be primarily for demonstration/educational purposes rather than production use