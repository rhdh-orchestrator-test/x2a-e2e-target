# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and integrating the Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations include converting to Ansible-compatible testing framework or maintaining InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations include converting to Ansible-compatible testing framework or maintaining InSpec integration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec (latest)**: Either maintain as a compliance testing tool alongside Ansible or replace with Ansible-native testing solutions
- **Vagrant (latest)**: Can be maintained for local testing or replaced with alternative virtualization solutions
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for equivalent functionality

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance this security posture.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider integrating with Let's Encrypt or other certificate authorities in the Ansible migration.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible implementation.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Integration**: Determining how to maintain compliance testing capabilities while migrating to Ansible. Options include:
  1. Continuing to use InSpec alongside Ansible
  2. Converting InSpec tests to Ansible-compatible testing frameworks
  3. Using Ansible's assert module for basic compliance checks

- **Chef Automate/Infra Server Replacement**: Deciding on an equivalent solution for the Chef server functionality:
  1. Using Ansible AWX/Tower as a replacement for Chef Automate
  2. Implementing a simpler Git-based workflow without a central server
  3. Maintaining Chef Automate but managing it with Ansible

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper structure (low risk, already in Ansible)
2. **poodle_fix.yml** (Priority 1): Convert to Ansible role or include in the website_https role (low risk, already in Ansible)
3. **InSpec Tests** (Priority 2): Decide on testing strategy and implement (moderate complexity)
4. **Chef Server Setup Scripts** (Priority 3): Replace with Ansible playbooks for equivalent functionality (higher complexity)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README indicating it provides examples related to content created by Technical Product Marketing.
2. The InSpec tests are intended to be run against systems configured by Ansible, demonstrating how Chef InSpec can be used for compliance testing alongside Ansible.
3. The Chef Automate and Chef Infra Server setup scripts are intended to demonstrate server setup rather than being part of a larger Chef-based infrastructure.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure values in a production environment.
5. The target environment is Ubuntu 20.04, but the Ansible playbooks may need to support additional distributions in the future.
6. The current implementation uses Vagrant for local testing, but the production environment could be different.