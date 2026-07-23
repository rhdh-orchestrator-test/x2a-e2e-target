# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

The repository appears to be primarily focused on examples and demonstrations rather than production infrastructure code. The migration complexity is **LOW** with an estimated timeline of **1-2 WEEKS** for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec Tests**: Maintain InSpec tests but integrate with Ansible using ansible_inspec module or convert to Ansible-native testing with Molecule
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: The repository includes InSpec tests for SSH security compliance.
  - Migration approach: Implement equivalent SSH hardening using Ansible's `openssh_config` module

- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: The repository uses InSpec for compliance testing alongside Ansible.
  - Mitigation strategy: Either maintain InSpec tests and integrate with Ansible using the `inspec` module, or convert tests to Ansible-native testing with Molecule

- **Chef Automate Replacement**: The deployment scripts set up Chef Automate and Chef Infra Server.
  - Mitigation strategy: Create Ansible playbooks to deploy AWX/Tower as a replacement for centralized management

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format, just need structural reorganization
2. **Testing Framework** (kitchen.yml and InSpec tests): Moderate complexity, requires setting up Molecule or integrating InSpec with Ansible
3. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity, requires creating equivalent Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The repository is primarily for demonstration purposes rather than production infrastructure
2. The InSpec tests are valuable and should be maintained or converted
3. A centralized management solution (like AWX/Tower) is needed to replace Chef Automate functionality
4. The target environment will continue to be Ubuntu-based systems
5. The self-signed certificates are acceptable for the use case (not production)
6. The hardcoded credentials in deployment scripts are for demonstration only and will be properly secured in the migrated solution