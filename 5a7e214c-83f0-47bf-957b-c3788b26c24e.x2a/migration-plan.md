# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of Chef Automate and Chef Infra Server deployment scripts, along with some existing Ansible playbooks and InSpec tests. The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **Chef Automate Deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: User creation, organization setup, system configuration

- **Chef Infra Server Deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: User creation, organization setup, system configuration

- **HTTPS Website Deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **SSL Poodle Vulnerability Fix**:
    - Description: Ansible playbook to fix SSL Poodle vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration testing with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Can be retained as a testing framework, as it's already being used with Ansible

### Security Considerations

- **SSH Root Login**: InSpec tests verify SSH root login is disabled (ssh_profile.rb)
- **SSL/TLS Configuration**: Ensure proper SSL protocols are enabled (TLS 1.2) and vulnerable protocols (SSL3) are disabled
- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - SSL certificates and keys generated and stored in /etc/apache2/certs/
  - Recommend using Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles that can configure equivalent functionality
- **InSpec Integration**: Ensure continued integration between Ansible and InSpec for compliance testing
- **System Requirements**: Maintain system configuration requirements (vm.max_map_count, vm.dirty_expire_centisecs)

### Migration Order

1. **HTTPS Website Deployment** (already in Ansible, no migration needed)
2. **SSL Poodle Vulnerability Fix** (already in Ansible, no migration needed)
3. **Chef Infra Server Deployment** (convert bash script to Ansible role)
4. **Chef Automate Deployment** (convert bash script to Ansible role)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. InSpec will continue to be used for compliance testing alongside Ansible
3. The Chef deployment scripts are intended to be replaced with equivalent Ansible functionality
4. The target environment will continue to be Ubuntu 20.04 or similar
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already functioning correctly and don't need migration