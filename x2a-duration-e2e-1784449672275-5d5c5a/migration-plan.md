# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec compliance testing

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the Chef Automate deployment scripts to Ansible playbooks while preserving the existing Ansible playbooks and adapting the InSpec tests to work within a pure Ansible environment.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Migration consideration: Keep as-is, but update to use Ansible collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Migration consideration: Keep as-is, but update to use Ansible collections.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS configuration. Migration consideration: Convert to Ansible Molecule tests or maintain InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule tests or maintain InSpec integration.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing or replace with Ansible-native solutions:
  - Option 1: Keep InSpec and integrate with Ansible using the `inspec` Ansible module
  - Option 2: Replace InSpec tests with Ansible Molecule tests
  - Option 3: Replace InSpec tests with Ansible assert modules and custom modules

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in `poodle_fix.yml` that disables SSLv3 and enables only TLSv1.2
- **SSH Hardening**: The SSH security profile in `ssh_profile.rb` must be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - SSL certificates generated in the Ansible playbook should use secure key management

### Technical Challenges

- **InSpec Integration**: Determining whether to maintain InSpec for compliance testing or migrate to Ansible-native solutions
  - Mitigation: Evaluate the complexity of the InSpec tests and determine if Ansible's built-in modules can provide equivalent functionality
  
- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef Automate and Chef Infra Server deployment with idempotent tasks

### Migration Order

1. **setup-automate scripts** (high value, moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management
   
2. **chef-and-ansible playbooks** (low risk, already in Ansible)
   - Update existing Ansible playbooks to use latest Ansible collections
   - Ensure idempotence and best practices
   
3. **InSpec tests** (moderate complexity)
   - Either integrate InSpec with Ansible or convert to Ansible-native testing

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the functionality of the existing Ansible playbooks
2. InSpec testing can either be maintained or replaced with Ansible-native solutions
3. The deployment scripts are targeting Ubuntu 20.04 environments
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management
5. The existing Ansible playbooks follow best practices and only need minor updates
6. The migration will maintain the same level of security compliance as the original configuration