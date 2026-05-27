# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol verification, SSH configuration verification

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but call it from Ansible using the command module

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH hardening tests must be preserved
  - Ensure root login remains disabled
  - Convert InSpec tests to equivalent Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible's assert module or integrate with Molecule for testing

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible automation
  - Mitigation: Create Ansible roles for deploying alternative compliance and automation tools

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **InSpec Tests** (convert to Ansible-native testing)
4. **Chef Deployment Scripts** (convert to Ansible roles)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance testing.
2. The Ansible playbooks (website_https.yml and poodle_fix.yml) are already in the target format and don't need migration.
3. The Chef InSpec tests need to be converted to Ansible-native testing mechanisms.
4. The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible roles.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
6. The target environment is Ubuntu 20.04 running on Vagrant VMs.
7. No external dependencies or complex configurations are present beyond what's visible in the repository.