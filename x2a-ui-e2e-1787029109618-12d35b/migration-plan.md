# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while standardizing their structure
3. Maintaining the Chef InSpec testing capabilities within the Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing framework
- **InSpec**: Maintain as a compliance testing tool, but integrate with Ansible workflow

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate/Server Deployment**: Converting the Chef deployment scripts to Ansible requires understanding of Chef Automate architecture.
  - Mitigation: Create Ansible roles that handle the installation and configuration of Chef products or their Ansible equivalents

- **InSpec Integration**: Maintaining InSpec tests while standardizing on Ansible.
  - Mitigation: Use Ansible's built-in integration with InSpec or convert tests to Ansible's assert module where appropriate

- **Test Kitchen**: Currently using Test Kitchen for Ansible testing.
  - Mitigation: Consider migrating to Molecule for Ansible role testing while maintaining InSpec for compliance testing

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** (high value, moderate complexity)
   - Convert bash scripts to Ansible roles
   - Implement Ansible Vault for credential management

2. **website_https** and **poodle_fix** (low risk, already in Ansible)
   - Standardize playbook structure
   - Implement role-based organization
   - Maintain InSpec testing integration

3. **Testing Framework** (moderate complexity)
   - Evaluate Test Kitchen vs. Molecule for Ansible testing
   - Ensure InSpec tests continue to work with the new structure

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Server deployment scripts are intended to be converted to Ansible rather than maintained as-is.
3. The InSpec testing capabilities are valuable and should be preserved in the Ansible workflow.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functional and can be used as a reference for the migration style.