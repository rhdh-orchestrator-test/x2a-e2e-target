# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and migrating Chef Automate/Infra Server setup scripts to Ansible roles. The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Integrate with Ansible using ansible-lint and continue using InSpec for compliance testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX

### Security Considerations

- **SSL Configuration**: The migration must maintain the secure SSL configuration (TLSv1.2 only) implemented in the poodle_fix.yml playbook
- **SSH Security**: The SSH security profile in ssh_profile.rb must be maintained in the migrated solution
- **Self-signed Certificates**: The certificate generation process should be maintained or improved
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely

### Technical Challenges

- **InSpec Integration**: Ensuring that InSpec tests continue to work with the migrated Ansible structure
- **Chef Server Migration**: Converting the Chef server setup scripts to Ansible roles will require understanding of Chef server architecture
- **Testing Framework**: Transitioning from Test Kitchen to Molecule will require test refactoring

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
2. **poodle-fix playbook** (low risk, already in Ansible format)
3. **InSpec test integration** (moderate complexity)
4. **Chef Automate/Server setup scripts** (higher complexity)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are essential and must be preserved in the migrated solution
3. The Chef Automate and Chef Infra Server setup scripts are used for setting up test environments
4. The hardcoded credentials in the setup scripts are not used in production environments
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The migration will focus on improving the structure and security of the existing Ansible playbooks
7. The existing Test Kitchen setup is used for testing the Ansible playbooks