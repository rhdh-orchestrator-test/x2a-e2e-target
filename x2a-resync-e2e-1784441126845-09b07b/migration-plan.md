# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with InSpec tests for validation
3. Test Kitchen configuration for integration testing

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec testing framework continues to function with the migrated infrastructure. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for integration testing - will need to be updated to work with pure Ansible
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website - can be retained with minor updates
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability - can be retained with minor updates
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website - can be retained
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance - can be retained
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate - needs to be replaced with Ansible playbook
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server - needs to be replaced with Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management solution
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **InSpec**: Retain for compliance testing, integrate with Ansible using the `community.general.inspec` module or post-task verification

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already addressed in poodle_fix.yml)
  - Maintain self-signed certificate generation or improve with Let's Encrypt integration
  
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement:
  - Ensure Ansible playbooks enforce the same SSH hardening measures
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup scripts

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible-only infrastructure
  - Mitigation: Use the `community.general.inspec` Ansible module to run InSpec tests as part of playbook execution
  
- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality
  - Mitigation: Evaluate Ansible AWX/Tower as a replacement for Chef Server's centralized management capabilities
  
- **Test Kitchen Replacement**: Ensuring test workflows remain functional
  - Mitigation: Implement Molecule testing framework for Ansible roles with similar capabilities to Test Kitchen

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Retain and update `website_https.yml` and `poodle_fix.yml`
   - Ensure they work without Chef dependencies

2. **InSpec Tests** (Low risk, can be used with Ansible)
   - Retain InSpec tests and integrate with Ansible using appropriate modules
   - Update test execution workflow to work without Test Kitchen

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace `deploy-automate.sh` and `deploy-chef-server.sh`
   - Implement Ansible Vault for credential management

4. **Test Kitchen Configuration** (Moderate complexity)
   - Replace Test Kitchen with Molecule for testing Ansible roles
   - Update CI/CD pipelines if present

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments
3. There are no external dependencies or integrations not visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar
5. There is no requirement to maintain backward compatibility with Chef-specific tools
6. The InSpec tests are valuable and should be retained in the migration
7. No custom Chef cookbooks or recipes are being used beyond what's visible in the repository
8. The hardcoded credentials in the setup scripts are for demonstration purposes only
9. The self-signed certificates are acceptable for the target environment