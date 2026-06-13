# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule with testinfra for more advanced testing
  - Option 4: Consider migrating to ansible-compliance if comprehensive compliance testing is required

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solutions:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security hardening measures are preserved in the migrated Ansible roles.
  - Migration approach: Create dedicated Ansible roles for Apache with SSL hardening

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the new testing framework.
  - Migration approach: Create Ansible assertions or testinfra tests to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the compliance requirements and finding equivalent testing methods.
  - Mitigation: Start with simple assertions and gradually build more complex tests

- **Chef Automate Functionality**: If Chef Automate is being used for compliance reporting, finding an equivalent in the Ansible ecosystem may be challenging.
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or consider integrating with third-party compliance tools

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing solutions
4. **Chef Deployment Scripts** (high complexity): Replace with Ansible playbooks for deploying alternative management platforms

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. The InSpec tests are used for compliance validation and their functionality needs to be preserved
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible automation
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The security requirements specified in the InSpec tests must be maintained
6. No external data sources or complex integrations are present in the current implementation
7. The repository is primarily for demonstration purposes rather than production use