# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring web servers with SSL
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef server deployment scripts to Ansible playbooks and ensuring the InSpec tests continue to work with the new Ansible-only approach. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring Apache web servers with SSL and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that hardens SSL configuration to prevent POODLE attacks. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Update to use Ansible-only approach.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations: Can be used as-is with Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Migration considerations: Can be used as-is with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Convert to Ansible playbook or remove if not needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Continue to use InSpec for compliance testing, but integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in testing capabilities

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in the poodle_fix.yml playbook
- **Self-signed certificates**: The website_https.yml playbook generates self-signed certificates; consider using Let's Encrypt for production
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled; ensure this security check is maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificates and keys in the Apache configuration
  - Recommend implementing Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require creating equivalent functionality for user and organization management
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible-only approach
- **Compliance Automation**: Maintaining the compliance automation workflow without Chef Automate

### Migration Order

1. Convert website_https.yml and poodle_fix.yml to use Ansible best practices (low risk, already in Ansible format)
2. Create Ansible playbooks for Chef Automate and Chef Infra Server deployment (moderate complexity)
3. Update kitchen.yml to use Ansible-only approach (low complexity)
4. Integrate InSpec tests with new Ansible playbooks (low complexity)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance automation
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The hardcoded credentials in the setup scripts are for demonstration purposes only
5. The self-signed certificates are for testing purposes only
6. The repository is intended for educational/demonstration purposes rather than production use