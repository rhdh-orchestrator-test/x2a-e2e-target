# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of Chef Automate and Chef Infra Server deployment scripts, along with some existing Ansible playbooks and InSpec tests. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer to complete the migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts using Chef CLI
    - Key Features: User creation, organization setup, server configuration

- **chef-and-ansible**:
    - Description: Ansible playbooks and InSpec tests for secure website deployment and compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with InSpec testing
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup, compliance testing

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website with Apache
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Can be retained as a compliance testing tool alongside Ansible

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL hardening (POODLE fix) that must be maintained
  - Migration approach: Convert to Ansible module for modifying SSL configuration
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible task to ensure SSH configuration is compliant

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - SSL certificates generated during deployment
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: The current deployment uses Chef-specific CLI tools
  - Mitigation: Research and implement equivalent Ansible roles for Chef Automate deployment or consider alternative configuration management platforms

- **InSpec Integration**: The current setup uses InSpec for compliance testing
  - Mitigation: Maintain InSpec for testing or migrate tests to Ansible-compatible testing frameworks

### Migration Order

1. **chef-and-ansible** (partially in Ansible format already, low risk)
   - First: poodle_fix.yml (already in Ansible format)
   - Second: website_https.yml (already in Ansible format)
   
2. **setup-automate** (high complexity, requires research for alternatives)

### Assumptions

1. The primary goal is to migrate away from Chef for infrastructure management while potentially retaining InSpec for compliance testing.
2. The current Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need significant changes.
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible roles or alternative solutions.
4. The hardcoded credentials in the deployment scripts are for testing purposes and will be replaced with secure credential management in production.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. Test Kitchen with Vagrant will continue to be used for testing, but with Ansible as the primary provisioner.