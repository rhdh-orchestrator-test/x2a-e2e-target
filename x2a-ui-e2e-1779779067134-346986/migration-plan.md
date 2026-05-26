# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to implement and verify compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework configuration.
- `index.html`: Sample HTML file, can be preserved as-is or included in Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Molecule with Testinfra for testing
  - **Option 2**: Ansible Molecule with Goss for testing
  - **Option 3**: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for:
  - Server installation
  - User and organization management
  - Configuration management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration preserves:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2)
  - Disabling of vulnerable protocols (SSL3)

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Root login restrictions
  - Compliance with STIG standards

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend using Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible-compatible testing frameworks:
  - Challenge: InSpec's resource-based testing model differs from procedural testing in Ansible
  - Mitigation: Use Molecule with Testinfra or Goss which provide similar declarative testing capabilities

- **Compliance Reporting**: InSpec provides built-in compliance reporting:
  - Challenge: Replicating compliance reporting capabilities in Ansible
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or use community modules for compliance reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **Testing Framework**: Set up Ansible Molecule to replace Test Kitchen
3. **InSpec Tests**: Convert InSpec tests to Ansible-compatible tests
4. **Chef Server Deployment Scripts**: Convert to Ansible roles and playbooks

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes.
2. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing.
3. There are no external Chef cookbooks or recipes being used that weren't visible in the repository.
4. The deployment scripts for Chef Automate/Infra Server are intended to be migrated to Ansible rather than preserved for deploying Chef infrastructure.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. There are no additional compliance requirements beyond what's specified in the existing InSpec tests.
7. The migration doesn't need to address scaling concerns as the examples appear to be for single-host deployments.