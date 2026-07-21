# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef server deployment scripts to Ansible playbooks

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily educational/demonstration in nature rather than a production infrastructure codebase.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Keep InSpec but integrate with Ansible using ansible_inspec module

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system requirements
  - Install Chef components if still needed
  - Create users and organizations

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in poodle_fix.yml
  - Ensure TLS 1.2 remains enabled and older protocols disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile must be preserved
  - Ensure root login remains disabled
  - Maintain audit trail capabilities

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificates and keys generated in the Apache configuration
  - Recommendation: Move credentials to Ansible Vault

### Technical Challenges

- **Test Framework Migration**: Converting InSpec tests to Ansible-compatible testing
  - Mitigation: Use ansible.builtin.assert or Molecule verify phase to implement equivalent tests

- **Self-signed Certificate Generation**: Ensuring the openssl operations are properly migrated
  - Mitigation: Use Ansible's crypto modules which are already in use in the existing playbooks

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (ssh_profile.rb, website_https_verify.rb) - Medium risk, requires framework change
3. Chef Server Deployment Scripts - Higher complexity, requires complete rewrite

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The existing Ansible playbooks are working correctly and don't need functional changes
3. There's no dependency on Chef-specific features that would be difficult to implement in Ansible
4. The InSpec tests are used for validation only and not integrated into a larger compliance framework
5. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with proper secret management in production
6. The target environment will continue to be Ubuntu 20.04 or compatible systems