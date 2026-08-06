# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

Given the limited scope and example nature of the repository, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response testing, SSL protocol verification

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. This file coordinates the testing of Ansible playbooks with InSpec tests.
- `README.md`: Documentation file explaining the purpose of the repository.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider maintaining InSpec as a complementary testing tool if its capabilities are required

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Server**: Replace with:
  - Ansible Tower/AWX for enterprise orchestration
  - Ansible Galaxy for role sharing
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. This should be preserved in the Ansible migration with potential improvements:
  - Use Ansible Vault for storing sensitive information
  - Update SSL protocols to current best practices (TLS 1.3 support)
  - Consider using Let's Encrypt integration instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH security configurations. This should be:
  - Implemented as Ansible tasks that apply the configuration
  - Verified with Ansible assert statements or Molecule tests

- **Credentials in Scripts**: The setup scripts contain hardcoded credentials:
  - In `deploy-automate.sh` and `deploy-chef-server.sh`, there are username/password variables
  - These should be moved to Ansible Vault or another secure secret management solution

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires:
  - Mapping InSpec resource types to Ansible modules
  - Converting test assertions to Ansible's syntax
  - Ensuring equivalent coverage and reporting

- **Deployment Script Conversion**: The Chef Automate/Server deployment scripts need to be:
  - Analyzed for idempotency concerns
  - Converted to Ansible tasks with proper error handling
  - Tested thoroughly to ensure equivalent functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need minor updates to follow best practices.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert these to Ansible-native testing solutions.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible roles/playbooks.
4. **Infrastructure Files** (kitchen.yml): Replace with Molecule configuration.

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use.
2. The InSpec tests are used for validation rather than continuous compliance monitoring.
3. There is no complex state management or data persistence requirements.
4. The deployment scripts are used for initial setup rather than ongoing management.
5. There are no external dependencies or integrations not visible in the repository.
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
7. The migration will maintain the same level of security validation as the original code.