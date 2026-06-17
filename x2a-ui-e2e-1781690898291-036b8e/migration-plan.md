# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed as it's a static asset.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set system parameters (sysctl)
  - Download and install required packages
  - Configure services
  - Create users and organizations

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure the Ansible-native testing solution can verify SSL protocols are properly configured.
  - Migration approach: Use Ansible's `uri` module with SSL verification options

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create Ansible tasks using the `assert` module to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Use Ansible's `assert` module with appropriate conditionals or consider using Molecule with testinfra for more test-oriented syntax.

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated.
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or implement custom reporting using Ansible's callback plugins.

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires understanding of Chef's architecture.
  - Mitigation: Create an Ansible role specifically for Chef server deployment that handles all the steps in the bash scripts.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks.
4. **Infrastructure Configuration** (kitchen.yml): Replace with Molecule configuration.

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks.
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
3. There are no external dependencies or integrations not visible in the provided files.
4. The Chef Automate and Chef Server deployment scripts are intended to be converted to Ansible rather than preserved.
5. No specific compliance framework requirements beyond what's explicitly mentioned in the InSpec tests.
6. The repository is primarily for demonstration/educational purposes rather than production use, based on the README description.