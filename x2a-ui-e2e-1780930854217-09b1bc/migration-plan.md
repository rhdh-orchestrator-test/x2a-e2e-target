# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already with Chef InSpec tests and Chef server deployment scripts.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port checking, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (vm.max_map_count, vm.dirty_expire_centisecs)
  - Install and configure alternative compliance and infrastructure management tools

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain the security hardening that disables vulnerable protocols.
  - Migration approach: Preserve the same SSL configuration in the Ansible playbooks

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or Molecule tests to verify SSH security

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the test logic and recreating it.
  - Mitigation: Use Molecule's verifier plugins or custom Ansible assertions to replicate InSpec tests

- **Chef Server Replacement**: Determining what components should replace Chef Automate/Server functionality.
  - Mitigation: Evaluate if AWX/Tower or other tools are needed to replace Chef Server functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Highest complexity, convert to Ansible playbooks
4. **Infrastructure Files** (kitchen.yml) - Replace with Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes.
3. There's no requirement to maintain backward compatibility with Chef InSpec after migration.
4. The deployment scripts are used for setting up test environments rather than production systems.
5. There are no external dependencies or integrations not visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
7. The target environment will continue to be Ubuntu 20.04 or compatible systems.