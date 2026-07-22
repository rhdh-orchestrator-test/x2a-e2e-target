# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts. The migration scope is relatively small, focusing on standardizing all components to Ansible. The primary work involves:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Migrating Chef Automate and Chef Server deployment scripts to Ansible playbooks
3. Ensuring existing Ansible playbooks follow best practices

Given the limited scope and small number of components, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing, STIG control verification

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and TLS security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response testing, SSL/TLS protocol testing

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Simple HTML test file used by the website_https playbook. Can be retained as-is or converted to a template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver section)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the Ansible `shell` module to run InSpec tests during a transition period

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing:
  - Molecule provides native Ansible testing capabilities
  - Supports multiple drivers including Vagrant
  - Integrates with various verifiers including Testinfra

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles:
  - Create roles for system preparation (hostname, sysctl settings)
  - Create roles for package installation and configuration
  - Use Ansible Vault for credential management

### Security Considerations

- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials:
  - In `deploy-automate.sh` and `deploy-chef-server.sh`, username/password variables should be moved to Ansible Vault
  - Create separate vault files for different environments

- **SSL/TLS Configuration**: 
  - The `poodle_fix.yml` playbook addresses SSL POODLE vulnerability
  - Ensure this security fix is incorporated into the main Apache configuration role
  - Consider using the `crypto_policy` module for system-wide crypto settings

- **SSH Security**: 
  - The `ssh_profile.rb` tests for SSH root login being disabled
  - Create an Ansible role for SSH hardening that implements this and other best practices
  - Add post-deployment verification using Ansible assert or Molecule

- **Vault/secrets management**: 
  - 2 instances of hardcoded credentials detected in Chef deployment scripts
  - No encrypted data bags or Chef Vault usage detected
  - Migration should use Ansible Vault for all sensitive data

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec provides more specialized testing capabilities than basic Ansible assertions
  - Consider using Testinfra with Molecule for more powerful testing capabilities
  - Mitigation: Create custom Ansible modules for specialized tests if needed

- **Maintaining Test Coverage**: Ensuring the same level of compliance testing:
  - The InSpec tests verify specific security controls (STIG requirements)
  - Ensure all compliance checks are preserved in the Ansible testing framework
  - Mitigation: Create a compliance verification matrix to track test coverage

### Migration Order

1. **website_https.yml** (Priority 1): Already in Ansible format, just needs review for best practices
2. **poodle_fix.yml** (Priority 1): Already in Ansible format, should be integrated into a comprehensive Apache role
3. **InSpec Tests** (Priority 2): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles and playbooks

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 with Vagrant for testing
2. No actual Chef cookbooks or recipes are in use, only InSpec tests and deployment scripts
3. The existing Ansible playbooks are functional and don't require significant rework
4. The team has experience with both Chef and Ansible technologies
5. No external Chef server or infrastructure is required for the migrated solution
6. The InSpec tests are used primarily for local verification rather than as part of a larger compliance framework
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only
8. The self-signed certificates are acceptable for the target environment (not production)