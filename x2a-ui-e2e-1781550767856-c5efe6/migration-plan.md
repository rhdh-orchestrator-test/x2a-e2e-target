# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule with Testinfra for more complex testing scenarios
  - Option 3: Integrate with other testing frameworks like ServerSpec or GOSS

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platforms

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH root login compliance check needs to be maintained in the new testing framework.
- **Self-signed Certificates**: The process for generating self-signed certificates should be preserved in the Ansible playbook.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (in deploy-automate.sh and deploy-chef-server.sh)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require mapping InSpec resources to equivalent testing constructs.
  - Mitigation: Create a mapping document for InSpec resources to Ansible testing modules/plugins.

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require understanding the Chef Automate installation process.
  - Mitigation: Create an Ansible role that performs equivalent steps to the bash scripts.

- **Test Kitchen to Molecule**: Converting Test Kitchen configuration to Molecule will require understanding the differences in configuration syntax.
  - Mitigation: Use Molecule templates and adapt them to match the current Test Kitchen workflow.

### Migration Order

1. **website_https.yml and poodle_fix.yml**: These are already Ansible playbooks and require minimal changes, possibly just refactoring into roles.
2. **InSpec Tests**: Convert the InSpec tests to Ansible-compatible testing frameworks.
3. **Chef Deployment Scripts**: Convert the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks.
4. **Test Infrastructure**: Replace Test Kitchen with Molecule for testing the Ansible roles.

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes.
2. The InSpec tests are currently being used with Test Kitchen to verify the Ansible playbooks.
3. The deployment scripts for Chef Automate and Chef Infra Server are used independently of the Ansible playbooks.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The security requirements specified in the InSpec tests (especially ssh_profile.rb) must be maintained in the migrated solution.
6. The repository appears to be a demonstration or example repository rather than a production codebase, based on the README content.
7. No external dependencies or integrations beyond what's visible in the repository are required for the migration.