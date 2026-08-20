# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the existing Ansible playbooks follow best practices
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible playbooks

Given the limited scope and relatively simple structure, this migration is estimated to be **LOW complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG/CCI)

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Static HTML content used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider Ansible's integration with pytest for advanced testing scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in inventory management for multi-node testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for configuration management
  - Consider AWX/Ansible Tower as a replacement for Chef Automate's UI and workflow capabilities

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these configurations are maintained and updated to current best practices.
  - Migration approach: Convert existing SSL configurations to use the Ansible `openssl_*` modules with up-to-date cipher configurations.

- **SSH Security**: The InSpec tests check for SSH root login restrictions. Ensure these security checks are maintained.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint rules to verify SSH configuration.

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials.
  - Migration approach: Replace with Ansible Vault for secure credential storage.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (2 instances)
  - No encryption or secure storage currently implemented

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Ansible's `assert` module with carefully crafted conditions that match InSpec's intent.

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated.
  - Mitigation: Consider integrating with tools like Ansible Tower/AWX for reporting or implement custom reporting using Ansible's callback plugins.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need review and potential refactoring to follow best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires converting to Ansible-compatible testing.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires full conversion from bash scripts to Ansible playbooks.

### Assumptions

1. The repository is primarily educational/demonstrative and not used in production environments.
2. The InSpec tests are intended to validate the configurations applied by the Ansible playbooks.
3. The deployment scripts are used for setting up test environments rather than production Chef installations.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. The migration will maintain the same functionality but using Ansible-native approaches.
7. No external dependencies or integrations beyond what's visible in the repository.
8. The kitchen.yml configuration is used for testing the Ansible playbooks with InSpec verification.