# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or incorporated into Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved in the migrated solution.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2 only) in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. This security check should be preserved.
  - Migration approach: Convert the InSpec test to an Ansible assertion or Molecule test.

- **Self-signed Certificates**: The current solution generates self-signed certificates. Consider enhancing with Let's Encrypt integration.
  - Migration approach: Use Ansible's `acme_certificate` module for Let's Encrypt integration.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible's testing capabilities may require additional logic.
  - Mitigation: Use Ansible's `assert` module with appropriate conditions or consider using Molecule for more advanced testing.

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires understanding of Chef server architecture.
  - Mitigation: Create Ansible roles that replicate the Chef server deployment steps, possibly using the `uri` module to interact with Chef APIs.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (Priority 1, low risk): These are already Ansible playbooks and require minimal changes, possibly just refactoring into roles.

2. **InSpec Tests** (Priority 2, moderate complexity): Convert the InSpec tests to Ansible-compatible testing frameworks.

3. **Chef Deployment Scripts** (Priority 3, high complexity): Convert the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require functional changes.

2. The InSpec tests are currently being used for compliance validation and these compliance requirements must be preserved in the Ansible migration.

3. The deployment scripts for Chef Automate and Chef Infra Server are intended to be replaced with equivalent Ansible functionality, not to deploy Chef infrastructure.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. There are no external dependencies or integrations not visible in the provided files.

6. The migration is focused on technology change rather than functional changes to the deployed applications.