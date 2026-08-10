# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks and InSpec tests into a cohesive Ansible structure
3. Preserving the compliance testing capabilities currently provided by InSpec

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with HTTPS and InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: SSL configuration, Apache web server setup, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing capabilities or integrate with Ansible using the `ansible.builtin.shell` module to run InSpec tests
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same configuration

### Security Considerations

- **SSL Configuration**: The migration must maintain the secure SSL configuration (TLSv1.2 only) present in the current Ansible playbooks
- **SSH Security**: The InSpec tests check for secure SSH configuration, which must be maintained in the Ansible migration
- **Credentials Management**: 
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup-automate scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions or maintaining InSpec as a separate testing tool
  - Mitigation: Use Ansible's assert module for basic tests and consider maintaining InSpec for complex compliance testing
  
- **Chef Automate Deployment**: Replicating the Chef Automate deployment process in Ansible
  - Mitigation: Create Ansible roles that download and configure the necessary Chef components

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor existing Ansible playbooks into proper roles and structure
   - Integrate InSpec tests with Ansible or convert to Ansible assertions

2. **Chef Deployment Scripts** (Moderate complexity)
   - Convert Bash scripts to Ansible playbooks
   - Move hardcoded credentials to Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content
2. The Chef Automate and Chef Infra Server deployment scripts are intended for on-premises or generic cloud VM deployment
3. The InSpec tests are an essential part of the workflow and should be preserved in some form
4. The existing Ansible playbooks are already well-structured and will require minimal refactoring
5. No external dependencies or integrations beyond what's visible in the repository