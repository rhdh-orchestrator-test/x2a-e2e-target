# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint and Ansible Molecule for testing
  - For security scanning: Consider OpenSCAP integration or Ansible security roles

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Migration approach: Preserve the SSL protocol restrictions in the Ansible tasks
  
- **SSH Security**: The SSH hardening profile needs to be implemented in Ansible
  - Migration approach: Convert InSpec SSH tests to Ansible tasks that enforce the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically but should use Ansible Vault for any sensitive parameters
  - Count of credentials detected: 5 (username, longusername, useremail, userpassword, orgname) in setup-automate scripts

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment to Ansible requires understanding of Chef Automate architecture
  - Mitigation: Create an Ansible role that installs and configures equivalent functionality or a different configuration management solution

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules and Molecule for testing, or integrate with other testing frameworks

### Migration Order

1. **chef-and-ansible** (low risk, already in Ansible)
   - Consolidate and optimize the existing Ansible playbooks
   - Replace InSpec tests with Ansible-native testing

2. **setup-automate** (moderate complexity)
   - Create Ansible roles to replace Chef Automate and Chef Infra Server functionality
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to move away from Chef tooling entirely, including Chef InSpec for testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functional and can be used as reference
3. The target environment will continue to be Ubuntu 20.04 or compatible
4. Vagrant will continue to be used for development/testing environments
5. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives
6. The organization requires maintaining the same level of security compliance currently tested by InSpec