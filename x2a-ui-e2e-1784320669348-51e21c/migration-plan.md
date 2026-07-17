# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations with a focus on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible testing framework or kept as InSpec.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be migrated to Ansible testing framework or kept as InSpec.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Should be replaced with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Ansible Lint for static code analysis
  - Molecule for Ansible role testing
  - Alternatively, maintain InSpec as a compliance tool alongside Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in `poodle_fix.yml` that disables vulnerable protocols
  - Migration approach: Maintain the same configuration in Ansible roles

- **SSH Security**: The SSH compliance profile in `ssh_profile.rb` checks for root login restrictions
  - Migration approach: Create equivalent Ansible role with proper SSH configuration and testing

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **Compliance Testing**: The repository demonstrates using Chef InSpec for compliance testing with Ansible
  - Mitigation: Either maintain InSpec as a compliance tool or migrate to Ansible-native testing solutions

- **Infrastructure Deployment**: The Chef Automate and Chef Infra Server deployment scripts need to be replaced
  - Mitigation: Create equivalent Ansible playbooks for infrastructure deployment, potentially using AWX/Tower

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible): `website_https.yml` and `poodle_fix.yml`
2. **Testing Framework** (Moderate complexity): Migrate from Test Kitchen to Molecule or maintain InSpec
3. **Infrastructure Deployment** (High complexity): Replace Chef Automate/Infra Server deployment scripts with Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec for compliance testing alongside Ansible, not for production use
2. The hardcoded credentials in the setup scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The migration will standardize on Ansible for configuration management while potentially maintaining InSpec for compliance testing
5. No actual Chef cookbooks or recipes are present in the repository, simplifying the migration
6. The SSL and HTTPS configurations are for demonstration purposes and may need enhancement for production use