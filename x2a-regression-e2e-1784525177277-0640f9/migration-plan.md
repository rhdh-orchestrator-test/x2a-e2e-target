# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec tests can still be used for compliance verification. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Update to use Ansible-native testing frameworks or adapt to work with pure Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration considerations: Determine if InSpec will be retained for testing or if tests should be migrated to Ansible-native testing tools.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH compliance. Migration considerations: Determine if InSpec will be retained for testing or if tests should be migrated to Ansible-native testing tools.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **InSpec**: Decision needed - either:
  1. Retain InSpec for compliance testing (recommended if already invested in InSpec)
  2. Replace with Ansible-native testing using assert, community.general.assert_cmd, or molecule

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in poodle_fix.yml
- **SSH Hardening**: The SSH compliance profile in ssh_profile.rb must be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificate generation and management
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Determining how to maintain compliance testing with InSpec or migrate to Ansible-native testing
  - Mitigation: If keeping InSpec, use the ansible_inspec module; if migrating, use Ansible assert or molecule
- **Chef Server Replacement**: Determining if Chef Server functionality needs to be replaced
  - Mitigation: Evaluate if AWX/Tower can provide the required functionality or if a simpler Ansible-based approach is sufficient

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Chef Deployment Scripts** (Moderate complexity)
   - deploy-chef-server.sh
   - deploy-automate.sh

3. **Testing Framework** (High complexity, dependencies)
   - InSpec tests
   - Test Kitchen configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments, not for production deployments.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The migration goal is to standardize on Ansible while maintaining the compliance testing capabilities currently provided by InSpec.
5. No actual Chef cookbooks or recipes are present in the repository that need migration.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and not used in production.