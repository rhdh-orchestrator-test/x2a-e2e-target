# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity for the Ansible playbooks and moderate complexity for replacing the InSpec tests with Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be kept as-is or included as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or other Ansible-compatible compliance tools

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for enterprise management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved in the migrated Ansible roles.
  - Migration approach: Create dedicated Ansible role for Apache SSL hardening

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are implemented in Ansible.
  - Migration approach: Create Ansible tasks to enforce SSH security settings and add assert statements to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 1 password (hardcoded)
    - chef-server-deployment: 1 password (hardcoded)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation strategy: Use Ansible's assert module with register for most checks, consider custom modules for complex validations

- **Chef Automate Replacement**: Replacing Chef Automate functionality with Ansible AWX/Tower will require planning for dashboard, reporting, and compliance features.
  - Mitigation strategy: Map Chef Automate features to AWX/Tower equivalents, identify gaps and plan for additional tools if needed

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Convert to Ansible roles for better reusability

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible security role with built-in validation

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Infra Server deployment
   - Implement Ansible AWX/Tower deployment playbook

### Assumptions

1. The primary purpose of this repository is demonstration and education rather than production use
2. The InSpec tests are used for validation after Ansible playbook execution
3. The deployment scripts are used for setting up Chef infrastructure, which would be replaced by Ansible infrastructure
4. No external dependencies or cookbooks are being used beyond what's visible in the repository
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No complex data bags or Chef environments are in use
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only