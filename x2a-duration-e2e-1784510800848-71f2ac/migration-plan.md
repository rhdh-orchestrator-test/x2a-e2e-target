# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation, along with Chef deployment scripts. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance and security configurations
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: A set of Ansible playbooks with Chef InSpec tests for configuring and validating HTTPS websites and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible playbooks with Chef InSpec tests
    - Key Features: HTTPS website configuration, SSL security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS websites. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Should be migrated to Ansible-compatible testing frameworks like Testinfra or Molecule.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configurations. Should be migrated to Ansible-compatible testing frameworks.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbooks for configuration management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be replaced with Ansible playbooks for configuration management.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - **Option 1**: Use Ansible's built-in `assert` module for simple tests
  - **Option 2**: Use Testinfra with pytest for more complex testing
  - **Option 3**: Use Molecule for comprehensive testing of Ansible roles

- **Test Kitchen**: Replace with Molecule for Ansible role testing and development

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management or consider other Ansible-compatible compliance tools

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure these configurations are preserved in the migration.
  - Migration approach: Preserve the existing Ansible tasks for SSL configuration.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Testinfra tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in playbooks
  - Migration approach: Replace hardcoded credentials with Ansible Vault for secure storage of sensitive information.

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Map InSpec resources to equivalent Testinfra or Molecule assertions.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality.
  - Mitigation strategy: Evaluate Ansible AWX/Tower or other compliance tools based on specific requirements.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Preserve existing playbooks (website_https.yml, poodle_fix.yml)
   - Update any deprecated syntax or modules

2. **InSpec Tests** (Moderate complexity)
   - Convert website_https_verify.rb to Testinfra or Molecule tests
   - Convert ssh_profile.rb to Testinfra or Molecule tests

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential storage

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and do not require significant changes.
3. The Chef InSpec tests are used for compliance verification rather than configuration management.
4. The setup-automate scripts are used for deploying Chef infrastructure, which will need to be replaced with equivalent Ansible functionality.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The target environment is Ubuntu 20.04 running on Vagrant VMs, as specified in kitchen.yml.
7. The migration will focus on preserving the functionality of the existing playbooks while replacing Chef-specific components with Ansible equivalents.