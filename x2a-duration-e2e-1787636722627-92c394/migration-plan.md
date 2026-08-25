# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with a focus on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring the existing Ansible playbooks follow best practices
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

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
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test that verifies HTTPS configuration. Will need to be converted to Ansible-compatible testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test that verifies SSH configuration security. Will need to be converted to Ansible-compatible testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks like:
  - Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - testinfra for infrastructure validation

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Or keep Test Kitchen but update configuration to work with pure Ansible

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Hardening**: The InSpec tests check for SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or testinfra tests.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef server deployment scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use testinfra which has similar syntax to InSpec, or implement custom Ansible tasks that perform the same checks.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible.
  - Mitigation: Create Ansible roles for Chef server deployment, or consider if Chef server is still needed after migration.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Update to follow best practices.
2. **Testing Framework**: Convert InSpec tests to Ansible-compatible testing frameworks.
3. **Deployment Scripts**: Convert Chef Automate/Infra Server deployment scripts to Ansible playbooks.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README content.
2. The Chef InSpec tests are used to validate configurations managed by Ansible, showing how the two technologies can work together.
3. After migration, Chef components (Automate, Infra Server) may no longer be needed, unless they serve specific compliance reporting purposes.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production environments.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
6. The migration will maintain the same functionality but using Ansible-native approaches.