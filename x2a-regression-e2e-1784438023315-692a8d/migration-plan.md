# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Consolidating the existing Ansible playbooks
2. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly reused in the migrated solution.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Can be directly reused in the migrated solution.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Should be migrated to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other compliance tools like CINC Auditor (open source InSpec)

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Determine if these components are still needed or if they can be replaced with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - CI/CD pipelines for automation

### Security Considerations

- **SSL/TLS Configuration**: The existing Ansible playbooks already implement proper TLS 1.2 configuration and disable insecure protocols. This should be preserved in the migration.

- **SSH Hardening**: The InSpec profile for SSH security should be converted to equivalent Ansible checks or integrated with an Ansible-compatible compliance tool.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef deployment scripts contain hardcoded passwords that should be moved to Ansible Vault
  - SSL certificates: The self-signed certificate generation should be preserved but potentially enhanced with Let's Encrypt integration

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches and possibly writing custom modules.
  - Mitigation: Start with simple assertions and gradually enhance the testing framework.

- **Chef Automate Replacement**: If Chef Automate functionality is still needed, determining the right Ansible-based replacement could be complex.
  - Mitigation: Evaluate AWX/Tower features against current Chef Automate usage to identify any gaps.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Consolidate and optimize existing Ansible playbooks (website_https.yml, poodle_fix.yml)
2. **Testing Framework** (Medium complexity): Migrate InSpec tests to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (High complexity): Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use, as indicated by the README.md.
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed with Ansible, suggesting a hybrid approach that could be consolidated to pure Ansible.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which may or may not be needed in the future Ansible-only approach.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.
5. There are no complex Chef cookbooks or recipes to migrate beyond the deployment scripts.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.