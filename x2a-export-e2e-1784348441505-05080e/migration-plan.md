# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-tests**:
    - Description: Chef InSpec test profiles for validating HTTPS website and SSH configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification, SSH security compliance

- **chef-automate-setup**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert tasks
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with Molecule for testing
  - Option 4: Retain InSpec as a standalone testing tool called from Ansible

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Playbook testing with ansible-test

- **Chef Automate/Infra Server**: Replace with Ansible automation controller:
  - Option 1: Ansible AWX (open source)
  - Option 2: Red Hat Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH hardening checks from the InSpec profile
  - Ensure root login remains disabled
  - Maintain compliance with security standards referenced in the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible.builtin.vault or external secret management

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing functionality currently provided by Chef InSpec
  - Solution: Either convert InSpec tests to Ansible assertions or maintain InSpec as a separate tool called from Ansible

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing
  - Solution: Replace with Molecule for Ansible role testing or create custom test orchestration

- **Chef Automate Functionality**: The Chef Automate deployment provides compliance reporting and visualization
  - Solution: Implement equivalent functionality using Ansible AWX/Tower with compliance plugins

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml) - Low risk, already in Ansible format
2. **InSpec Tests** (chef-and-ansible/tests/website_https_verify.rb, chef-and-ansible/tests/ssh_profile.rb) - Convert to Ansible assertions or integrate with Molecule
3. **Chef Deployment Scripts** (setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh) - Convert to Ansible roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The target environment will continue to be Ubuntu 20.04 as specified in the kitchen.yml
3. The security compliance requirements (SRG-OS-000112, V-38607, etc.) will remain relevant in the migrated solution
4. The migration will consolidate all functionality into Ansible rather than maintaining a hybrid approach
5. Test Kitchen functionality will need to be replaced with an Ansible-native testing solution
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution