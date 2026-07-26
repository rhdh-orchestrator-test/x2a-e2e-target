# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests as a compliance verification layer

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for deploying and testing a secure web server
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration against POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for verifying SSH security configuration
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as a compliance testing tool, no need to replace with Ansible equivalent
- **Test Kitchen with Ansible**: Update to use Ansible-native testing frameworks like Molecule
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening for web servers (POODLE vulnerability mitigation)
  - Migration approach: Preserve the same SSL configuration in Ansible tasks
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Add Ansible tasks to enforce SSH hardening alongside testing

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible deployments
  - Mitigation: Use Ansible's `shell` or `command` modules to execute InSpec tests, or integrate with CI/CD pipeline

- **Test Kitchen Replacement**: Moving from Test Kitchen to Ansible-native testing
  - Mitigation: Implement Molecule for Ansible role/playbook testing

### Migration Order

1. **setup-automate scripts** (high value, moderate complexity)
   - Convert shell scripts to Ansible playbooks
   - Implement Ansible Vault for credential storage
   - Add idempotency to ensure repeatable deployments

2. **Existing Ansible playbooks** (low risk, high value)
   - Review and optimize existing playbooks
   - Implement Ansible best practices (roles, variables, etc.)
   - Ensure compatibility with the latest Ansible versions

3. **Testing Framework** (moderate complexity)
   - Migrate from Test Kitchen to Molecule
   - Preserve InSpec tests as compliance verification

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments
2. Chef InSpec will continue to be used for compliance testing alongside Ansible
3. The hardcoded credentials in setup scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The existing Ansible playbooks are functional and follow best practices
6. The migration will maintain backward compatibility with existing test cases