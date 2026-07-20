# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Maintaining Chef InSpec tests as a compliance verification layer
4. Ensuring the migration preserves security configurations and testing capabilities

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing for secure web server deployment
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule or maintain as-is for InSpec testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Migration consideration: Keep as-is, it's already Ansible.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Migration consideration: Keep as-is, it's already Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as compliance testing tool, integrate with Ansible workflows

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening (poodle_fix.yml) that must be preserved in the migration
- **Self-signed certificates**: The website_https.yml playbook generates self-signed certificates that should be maintained
- **SSH hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled, which should be enforced in Ansible
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup-automate scripts

### Technical Challenges

- **Chef InSpec Integration**: Maintaining Chef InSpec for compliance testing while migrating to pure Ansible requires careful integration planning
- **Test Kitchen to Ansible Testing**: Converting Test Kitchen workflow to Ansible-native testing tools like Molecule
- **Credential Management**: Moving from hardcoded credentials to Ansible Vault or other secure storage

### Migration Order

1. **chef-and-ansible Ansible playbooks** (low risk, already Ansible): Minimal changes needed, focus on testing framework
2. **setup-automate deployment scripts** (moderate complexity): Convert Bash scripts to Ansible playbooks with proper credential management

### Assumptions

1. The Chef InSpec tests are intended to be kept as the compliance verification layer
2. The repository is primarily for demonstration purposes (based on README.md mentioning "examples")
3. The hardcoded credentials in setup scripts are not for production use
4. The target environment is Ubuntu 20.04 based on kitchen.yml configuration
5. The deployment is intended for on-premises or generic cloud VMs
6. There are no external dependencies or integrations beyond what's visible in the repository
7. The Chef Automate and Chef Infra Server deployments are standalone and not part of a larger Chef ecosystem
8. The SSL/TLS hardening is a critical security requirement that must be maintained