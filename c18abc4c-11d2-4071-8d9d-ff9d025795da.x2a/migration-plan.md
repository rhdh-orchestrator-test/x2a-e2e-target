# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of Chef Automate and Chef Infra Server deployment scripts, along with some existing Ansible playbooks and InSpec tests. The estimated timeline for migration is 1-2 weeks, with low complexity as many components are already in Ansible format.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, server configuration

- **chef-and-ansible**:
    - Description: Ansible playbooks and InSpec tests for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible and InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Can be retained as Ansible can use InSpec for compliance testing

### Security Considerations

- **SSH Root Login**: InSpec tests verify SSH root login is disabled (ssh_profile.rb)
- **SSL/TLS Configuration**: Ensure proper TLS protocols (disabling SSLv3, enabling TLSv1.2)
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates and keys generated and stored in /etc/apache2/certs
  - Recommend implementing Ansible Vault for credential storage

### Technical Challenges

- **Chef Server Deployment**: Creating an equivalent Ansible role for Chef Server deployment
  - Mitigation: Develop an Ansible role that installs and configures required packages
- **User and Organization Management**: Replicating Chef's user and organization management in Ansible
  - Mitigation: Create custom Ansible modules or use existing community modules

### Migration Order

1. **setup-automate** (high priority, moderate complexity)
   - This is the core Chef-specific component that needs migration
   - Create Ansible roles to replace the bash scripts for Chef Automate and Chef Server deployment

2. **chef-and-ansible** (low risk, already using Ansible)
   - Review and optimize existing Ansible playbooks
   - Ensure they follow best practices and are properly documented
   - Retain InSpec tests but integrate them with Ansible using ansible-test or direct InSpec calls

### Assumptions

1. The repository is primarily used for demonstration and educational purposes rather than production deployment
2. InSpec will continue to be used for compliance testing after migration
3. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already in the target format and only need review
4. The primary migration effort will focus on replacing the Chef Automate and Chef Infra Server deployment scripts
5. No complex Chef cookbooks or recipes are present in the repository
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. No external Chef dependencies or community cookbooks are being used