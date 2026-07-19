# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible solution. The primary components are:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for web server configuration with InSpec testing
3. Chef InSpec profiles for compliance testing

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The main effort will be in replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks, and ensuring the InSpec testing framework is properly integrated with Ansible.

**Estimated Timeline**: 2-3 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly reused in the migrated solution.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly reused in the migrated solution.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be maintained for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be maintained for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be replaced with Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible workflow
- **Test Kitchen**: Replace with Molecule for Ansible-native testing
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or alternative configuration management solution

### Security Considerations

- **SSL/TLS Configuration**: The repository contains specific SSL/TLS security configurations (POODLE vulnerability fix) that must be preserved in the migration
- **SSH Security**: InSpec tests for SSH security compliance must be maintained
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider implementing proper certificate management
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL/TLS certificate references in Apache configuration
  - Count: 2 credential sets detected (user login, SSL certificates)

### Technical Challenges

- **Compliance Testing Integration**: Ensuring InSpec tests continue to work with the new Ansible-only workflow
- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality (Ansible AWX/Tower, other tools)
- **Testing Framework Migration**: Moving from Test Kitchen to Molecule or another Ansible-native testing framework

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Integration** (Medium complexity)
   - Integrate existing InSpec tests with Ansible workflow
   - Replace Test Kitchen with Molecule

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace `deploy-automate.sh` and `deploy-chef-server.sh`
   - Determine if Chef Automate/Infra Server is still needed or can be replaced with Ansible AWX/Tower

### Assumptions

1. The primary goal is to consolidate on Ansible as the sole configuration management tool
2. Chef InSpec will still be used for compliance testing
3. The hardcoded credentials in the setup scripts are for testing purposes only
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The Apache HTTPS configuration requirements will remain the same
7. The organization may still need Chef Automate functionality (dashboards, reporting) which may require additional tools when migrating to Ansible-only
8. The SSL/TLS security requirements (TLS 1.2, disabled SSLv3) will remain in place