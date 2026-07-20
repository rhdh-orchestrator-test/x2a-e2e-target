# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be standardized and integrated into a cohesive Ansible framework

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer or 3-5 days for a small team. The primary challenge will be replacing Chef InSpec testing with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and InSpec tests
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec testing
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an Apache web server with HTTPS. Migration considerations include converting to an Ansible role structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Should be integrated into a comprehensive security role.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Sample HTML file for website testing. Can be directly used in Ansible content.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible testing framework.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Implement Molecule for comprehensive testing
  - Option 3: Consider ansible-lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - CI/CD pipeline integration for automated testing

### Security Considerations

- **SSL Configuration**: The existing playbooks properly configure TLS 1.2 and disable insecure protocols. This security hardening should be maintained in the migrated solution.

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. This security check should be implemented in the Ansible playbooks using the ansible.posix.sshd module.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbooks; consider using ansible-vault for storing production certificates

### Technical Challenges

- **Testing Framework Migration**: Moving from Chef InSpec to Ansible-native testing will require learning new testing patterns and possibly rewriting tests.
  - Mitigation: Start with simple assert module tests and gradually implement more complex testing as needed.

- **Chef-specific Functionality**: The Chef Automate and Chef Infra Server deployment scripts contain Chef-specific commands that need Ansible equivalents.
  - Mitigation: Research Ansible modules for system configuration and package management to replace Chef-specific commands.

### Migration Order

1. **chef-and-ansible** (low risk, already partially in Ansible): 
   - Convert individual playbooks to roles
   - Replace InSpec tests with Ansible testing
   - Standardize variable naming and structure

2. **chef-automate-deployment** (high complexity): 
   - Create new Ansible playbooks to replace Chef deployment scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies, not to change the functionality of the deployed applications.
2. The InSpec tests are considered valuable and their functionality should be preserved in the Ansible migration.
3. The Chef Automate and Chef Infra Server deployment is being replaced with an Ansible-based solution, not just being deployed by Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The migration will maintain or improve the security posture defined in the InSpec tests.
6. No additional functionality beyond what's in the current repository is required for the migration.