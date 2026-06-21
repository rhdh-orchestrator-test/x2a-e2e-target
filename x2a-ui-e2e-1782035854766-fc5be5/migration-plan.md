# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server. Can be preserved as-is or included in Ansible content.

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
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or Ansible's own testing frameworks

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration preserves the security settings, particularly:
  - SSL protocol restrictions (TLSv1.2 only)
  - Certificate generation and management
  
- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are preserved in the Ansible testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's testing capabilities may require additional scripting or integration with other testing frameworks.
  - Mitigation: Consider using Ansible's assert module combined with command/shell modules to run similar checks, or integrate with Molecule for more comprehensive testing.

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks will require knowledge of Chef server architecture.
  - Mitigation: Create Ansible roles that perform equivalent tasks, using the existing scripts as a reference.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These can remain largely unchanged, with minor adjustments to follow best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-compatible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks.
4. **Infrastructure Files** (kitchen.yml): Replace with Ansible-native testing configuration.

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant changes.
2. The team has expertise in both Chef InSpec and Ansible to understand the testing requirements.
3. The deployment scripts are used for setting up test environments and not production systems, given the hardcoded credentials.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration is primarily focused on standardizing on Ansible rather than addressing functional changes.
6. The InSpec tests are currently being used for compliance validation and these compliance requirements must be preserved in the Ansible solution.
7. There is no integration with external systems or services beyond what's explicitly mentioned in the files.