# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing with Ansible configurations and Chef infrastructure deployment scripts. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for configuring and validating HTTPS websites with Apache and SSL security fixes
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly used in Ansible migration with minor updates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly used in Ansible migration with minor updates.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website configuration. Should be migrated to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be migrated to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Should be replaced with Ansible playbook for infrastructure setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or other compliance tools

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Determine if these components are needed in the new architecture:
  - If yes: Replace with Ansible AWX/Tower for centralized management
  - If no: Remove these components entirely

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening in `poodle_fix.yml`
  - Approach: Preserve the existing Ansible task that enforces TLSv1.2
  
- **Self-signed Certificates**: The playbook generates self-signed certificates
  - Migration approach: Maintain this functionality but consider adding option for proper CA-signed certificates

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Migration approach: Create Ansible tasks to enforce the same SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for functional tests and consider integrating with compliance tools like OpenSCAP for more complex compliance testing

- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server deployment scripts
  - Mitigation: Create Ansible roles for infrastructure setup, potentially integrating with AWX/Tower for centralized management

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **Testing Framework** (Moderate complexity)
   - Replace Test Kitchen with Molecule
   - Convert InSpec tests to Ansible-native testing

3. **Infrastructure Deployment** (High complexity)
   - Replace Chef Automate/Infra Server deployment scripts with Ansible roles

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production use
2. The Chef InSpec tests are used for validation and compliance checking, not for configuration management
3. The deployment scripts are examples and may need customization for actual production environments
4. The migration will standardize on Ansible as the single configuration management and compliance tool
5. The existing Ansible playbooks are functional and follow best practices
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. Vagrant will continue to be used for local development and testing
8. The migration will address the hardcoded credentials in the deployment scripts