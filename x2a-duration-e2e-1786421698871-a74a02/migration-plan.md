# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure and migrating Chef InSpec tests to Ansible's testing capabilities. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerability by disabling older protocols and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page for the web server. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing capabilities or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Determine if these components need to be replaced with Ansible Tower/AWX or if they're just examples

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure proper SSL settings are maintained during migration.
- **SSH Hardening**: The InSpec tests verify SSH security settings. Ensure these checks are maintained in the Ansible testing framework.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks (Molecule, assert tasks, or other testing tools)
- **Test Kitchen to Molecule**: Adapting the testing workflow from Test Kitchen to Ansible Molecule
- **Chef Server Scripts**: Determining if the Chef server setup scripts need to be converted to Ansible roles or if they're just examples

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Standardize the playbook structure and integrate with Ansible best practices
2. **poodle_fix.yml** (low risk, already Ansible): Standardize the playbook structure and integrate with Ansible best practices
3. **InSpec Tests** (moderate complexity): Convert to Ansible-compatible testing framework
4. **Chef Server Setup Scripts** (if needed): Convert to Ansible roles for infrastructure setup

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can be used alongside Ansible
2. The actual infrastructure being managed is relatively simple (web servers with SSL)
3. There's no complex state management or data persistence requirements
4. The Chef Automate and Chef Infra Server setup scripts may not need migration if they're just examples
5. No external inventory or variable files are being used beyond what's visible in the repository
6. No complex role or collection dependencies exist
7. The target environment is Ubuntu 20.04 as specified in kitchen.yml