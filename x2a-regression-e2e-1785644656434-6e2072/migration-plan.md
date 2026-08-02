# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used for testing web server configuration. Can be reused as-is.

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

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Consider using ansible-navigator for local development

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved in the migrated playbooks.
  - Migration approach: Directly port the SSL configuration from the existing Ansible playbooks.

- **SSH Hardening**: The InSpec tests verify SSH security settings. Ensure these checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests.

- **Vault/secrets management**: 
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault.
  - SSL certificates are generated on the fly in the playbooks, which is a good practice to maintain.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules.

- **Chef Server Deployment**: The Chef Server deployment scripts contain specific Chef commands that need Ansible equivalents.
  - Mitigation: Research Ansible roles that can deploy similar infrastructure management tools or create custom roles.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity to convert to Ansible testing frameworks.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Highest complexity as they involve replacing Chef infrastructure components with Ansible equivalents.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README indicating these are examples related to blog content.
2. The Chef InSpec tests are used for validating configurations managed by Ansible, suggesting a hybrid approach is already in place.
3. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
4. The deployment scripts for Chef Automate and Chef Server are intended for setting up test environments rather than production infrastructure.
5. No actual Chef cookbooks or recipes are present in the repository, only InSpec tests and deployment scripts.
6. The migration goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment.