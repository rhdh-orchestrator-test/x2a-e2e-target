# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance profiles and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration/example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and example nature of the repository, this migration is estimated to be **LOW complexity** with an estimated timeline of **1-2 weeks** for a single engineer.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Simple HTML template for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD with Ansible for automation

### Security Considerations

- **SSL Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Approach: Ensure the same SSL protocol restrictions are applied in the migrated Ansible roles
  
- **SSH Security**: The SSH compliance checks must be preserved
  - Approach: Convert InSpec tests to Ansible assert statements or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
    - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Challenge 1: InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for simple tests, or integrate with Molecule for more complex testing scenarios
  
- **Challenge 2: Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform the same server setup and configuration

### Migration Order

1. **website_https.yml** (already Ansible, low risk)
2. **poodle_fix.yml** (already Ansible, low risk)
3. **InSpec tests** (moderate complexity, convert to Ansible testing framework)
4. **Chef deployment scripts** (higher complexity, convert to Ansible roles)

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The target environment will continue to be Ubuntu 20.04 or similar
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements will remain the same after migration
5. No external Chef cookbooks or complex Chef-specific features are being used
6. The self-signed certificates approach is acceptable for the migrated solution