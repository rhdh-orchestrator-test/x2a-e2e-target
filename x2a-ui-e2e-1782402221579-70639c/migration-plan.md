# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks demonstrating compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that need to be migrated to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low to medium complexity due to the limited scope and clear separation of concerns between the testing framework (Chef InSpec) and the configuration management tool (Ansible).

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible's built-in `assert` module for basic testing
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Use Ansible to run InSpec tests (keeping InSpec as a dependency)

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible automation controller (AWX/Tower) or other CI/CD tools

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible playbooks

- **SSH Hardening**: The SSH security controls need to be preserved
  - Approach: Convert InSpec tests to Ansible assert statements or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - chef-automate-setup: 3 credentials (username, password, organization)
    - chef-server-setup: 3 credentials (username, password, organization)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with careful validation to ensure equivalent test coverage

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible-native approaches
  - Mitigation: Identify which Chef Server features are actually being used and map to Ansible alternatives

### Migration Order

1. Convert InSpec tests to Ansible-compatible tests (low risk, foundation for validation)
   - website_https_verify.rb → Ansible assert or Molecule test
   - ssh_profile.rb → Ansible assert or Molecule test

2. Preserve existing Ansible playbooks with minimal changes (low complexity)
   - website_https.yml
   - poodle_fix.yml

3. Convert Chef Automate/Server setup scripts to Ansible playbooks (moderate complexity)
   - deploy-automate.sh → Ansible playbook
   - deploy-chef-server.sh → Ansible playbook

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The Chef InSpec tests are used primarily for validation and not for remediation
3. There's no direct dependency between the Chef Automate/Server setup and the Ansible playbooks
4. The target environment will continue to be Ubuntu 20.04 LTS
5. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure alternatives
6. The repository is primarily for demonstration/educational purposes rather than production use
7. No additional Chef cookbooks or resources are being used beyond what's visible in the repository