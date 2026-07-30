# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are preserved in the new implementation

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing.
- `index.html`: Simple HTML file used for testing the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the ansible_playbook provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for enterprise automation platform
  - Or use ansible-navigator for a lighter-weight solution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration preserves:
  - Proper certificate generation
  - Secure protocol settings (TLSv1.2)
  - Disabled vulnerable protocols (SSLv3)

- **SSH Hardening**: The InSpec profile checks SSH root login settings. Ensure:
  - SSH hardening checks are preserved in Ansible
  - Compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic.
  - Mitigation: Create a test mapping document to ensure all compliance checks are preserved.

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation: Use Ansible roles to modularize the deployment process.

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already Ansible playbooks, minimal changes needed
2. **InSpec Tests**: Convert to Ansible-native testing solutions
3. **Chef Deployment Scripts**: Convert to Ansible playbooks

### Assumptions

1. The primary goal is to move all functionality to Ansible, eliminating Chef dependencies.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and can be preserved with minimal changes.
3. The compliance checks in the InSpec tests are still relevant and should be maintained in the Ansible implementation.
4. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible playbooks that deploy alternative solutions.
5. Test Kitchen can be replaced with Molecule or another Ansible-native testing framework.
6. The target environment (Ubuntu 20.04) will remain the same after migration.