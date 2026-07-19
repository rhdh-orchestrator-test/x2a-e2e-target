# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 2-3 weeks, primarily due to the need to recreate Chef server functionality in Ansible and ensure proper integration of compliance testing.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server setup, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with AWX/Ansible Tower or other Ansible management platform
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `inspec_exec` module or convert to Ansible assert statements

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening in `poodle_fix.yml` that disables vulnerable protocols
- **SSH Hardening**: Maintain SSH security controls tested by `ssh_profile.rb`
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Self-signed certificates in the Apache configuration
  - Recommend migrating to Ansible Vault for credential storage

### Technical Challenges

- **Chef Server Replacement**: Determining the appropriate Ansible management platform (AWX/Tower) to replace Chef Server functionality
- **Compliance Testing Integration**: Ensuring InSpec tests are properly integrated into the Ansible workflow
- **Certificate Management**: Implementing proper certificate management for the HTTPS configuration

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Standardize existing playbooks
   - Integrate with Ansible best practices (roles, collections)
   - Maintain InSpec testing integration

2. **Chef Deployment Scripts** (Medium complexity)
   - Create Ansible roles for Chef Automate/Server functionality
   - Implement credential management with Ansible Vault
   - Develop equivalent user/organization management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The hardcoded credentials in deployment scripts are for demonstration purposes only
3. The self-signed certificates are acceptable for the target environment
4. The migration will maintain InSpec for compliance testing rather than converting to pure Ansible
5. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
6. There are no external dependencies or integrations not visible in the repository
7. The Apache configuration is relatively simple and doesn't include complex customizations
8. The Chef server deployment is for a small-scale environment based on the simple configuration