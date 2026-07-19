# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with InSpec testing
3. InSpec compliance profiles for security validation

The migration complexity is **LOW to MEDIUM** as most components are already in Ansible format, with the main effort focused on replacing Chef Automate/Infra Server functionality with Ansible alternatives. Estimated timeline: 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration consideration: Can be directly used in Ansible.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Migration consideration: Can be directly used in Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Migration consideration: Convert to Ansible test or maintain InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security. Migration consideration: Convert to Ansible test or maintain InSpec integration.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script. Migration consideration: Replace with Ansible AWX/Tower deployment.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script. Migration consideration: Replace with Ansible AWX/Tower deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate**: Replace with Ansible AWX or Tower for web UI, role-based access control, and job scheduling
- **Chef Infra Server**: Replace with Ansible AWX/Tower or GitOps workflow for configuration management
- **Chef InSpec**: Options include:
  1. Maintain InSpec for compliance testing (Ansible can execute InSpec)
  2. Replace with Ansible-native testing using ansible-test
  3. Migrate to alternative like OVAL or OpenSCAP

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening (poodle_fix.yml) that must be preserved in migration
- **Self-signed certificates**: Current implementation generates self-signed certificates; consider integrating with proper certificate management
- **SSH Hardening**: InSpec profile for SSH security must be maintained or converted to Ansible
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain InSpec or migrate to Ansible-native testing
  - Mitigation: Ansible can execute InSpec tests directly, allowing phased migration
- **User Management**: Chef user and organization management needs Ansible equivalent
  - Mitigation: Implement with Ansible AWX/Tower RBAC or custom Ansible roles
- **Test Kitchen**: Current testing uses Test Kitchen with Vagrant
  - Mitigation: Migrate to Ansible Molecule for testing infrastructure

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Medium complexity)
   - Convert kitchen.yml to Molecule
   - Decide on InSpec integration strategy

3. **Chef Deployment Scripts** (High complexity)
   - Replace Chef Automate/Infra Server with Ansible AWX/Tower
   - Implement user/organization management

### Assumptions

1. The current setup uses Chef primarily for infrastructure deployment and Ansible for configuration management
2. InSpec is used for compliance testing and could potentially be maintained
3. No complex Chef cookbooks or recipes are present that would require significant rewriting
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distribution
5. The deployment is for a relatively small environment (based on simple scripts)
6. No complex data bags or Chef Vault usage is present
7. The migration will need to address hardcoded credentials in deployment scripts
8. Test Kitchen with Vagrant is the current testing methodology
9. The Apache configuration is relatively standard and can be directly used in Ansible