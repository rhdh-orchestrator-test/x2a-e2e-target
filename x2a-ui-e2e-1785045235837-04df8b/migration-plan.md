# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and integrating Chef InSpec tests into an Ansible-native testing framework. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible templates.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Integrate InSpec with Ansible using the `inspec` Ansible module
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice by:
  - Using Ansible Vault for storing sensitive information
  - Implementing proper certificate management
  - Ensuring TLS 1.2+ is enforced (as in the poodle_fix.yml playbook)

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this security check in the new testing framework
  - Implement equivalent SSH hardening in Ansible roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing frameworks may require additional effort to maintain the same level of compliance validation.
  - Mitigation: Consider using the Ansible `inspec` module as an interim solution before full conversion.

- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Infra Server deployment need to be converted to Ansible roles.
  - Mitigation: Create dedicated Ansible roles for Chef infrastructure deployment, or consider if this functionality is still needed post-migration.

### Migration Order

1. **website_https.yml** (Priority 1): Already in Ansible format, requires minimal changes to convert to a proper Ansible role structure.
2. **poodle_fix.yml** (Priority 1): Simple playbook that can be easily integrated into the website_https role.
3. **InSpec Tests** (Priority 2): Convert to Ansible Molecule tests or integrate using the inspec Ansible module.
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles if still needed, or consider deprecating if moving away from Chef entirely.

### Assumptions

1. The repository is primarily used for demonstration purposes (as indicated by the README.md) rather than production deployments.
2. The Chef InSpec tests are intended to validate the Ansible playbook configurations.
3. The setup-automate scripts are used for setting up a Chef infrastructure environment, which may not be needed if fully migrating to Ansible.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.
5. No external inventory or variable files are present, suggesting simple testing scenarios rather than complex multi-environment deployments.
6. No complex role structure or dependencies exist in the current Ansible implementation.