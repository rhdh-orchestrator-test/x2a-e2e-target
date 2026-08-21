# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Refactoring existing Ansible playbooks to follow best practices
3. Converting Chef server deployment scripts to Ansible playbooks

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily focused on examples and demonstrations rather than production infrastructure code.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **website-https-compliance**:
    - Description: Chef InSpec test for verifying HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port checking, HTTP response validation, SSL protocol verification

- **ssh-compliance**:
    - Description: Chef InSpec test for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles
  - Option 2: Ansible Lint for static code analysis
  - Option 3: Maintain InSpec as a testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Option 1: Ansible Molecule for testing
  - Option 2: Simple Vagrant/Docker workflows with direct Ansible provisioning

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve security settings:
  - Ensure TLSv1.2 or higher is enforced
  - Disable weak ciphers
  - Implement proper certificate management

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure SSH hardening is maintained in Ansible playbooks
  - Implement equivalent checks in Ansible-compatible testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in bash scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username, password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework:
  - Mitigation: Use Ansible Molecule with Testinfra or maintain InSpec as a separate testing tool

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible:
  - Mitigation: Create Ansible roles for Chef server deployment or consider if Chef server is still needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need refactoring to follow best practices
2. **InSpec Tests**: Moderate complexity, requires converting to Ansible-compatible testing framework
3. **Chef Server Deployment Scripts**: Higher complexity, requires converting bash scripts to Ansible roles

### Assumptions

1. The repository is primarily for demonstration purposes rather than production infrastructure
2. The InSpec tests are used for compliance verification of infrastructure deployed by Ansible
3. The Chef server deployment scripts may not be needed if the migration is fully to Ansible
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or variable hierarchies are in use
7. No existing Ansible inventory or group variables are defined
8. The examples are standalone and not part of a larger infrastructure codebase