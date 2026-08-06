# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that are already using Chef InSpec for compliance testing
3. Standardizing on Ansible as the single configuration management tool

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most configuration already in Ansible

## Module Migration Plan

This repository contains Bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Chef InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing of Ansible playbooks. Keep using InSpec for testing but integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assert module for simpler tests.
- **Test Kitchen**: Currently used for testing Ansible playbooks. Consider migrating to Molecule for Ansible-native testing or keep using Test Kitchen with the `kitchen-ansible` plugin.
- **Chef Automate/Infra Server**: The deployment scripts need to be replaced with Ansible playbooks or removed if Chef infrastructure is no longer needed.

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL protocols and ciphers are maintained during migration.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider using Let's Encrypt or other trusted certificates in production.
- **Hardcoded Credentials**: 
  - The Chef deployment scripts contain hardcoded usernames and passwords that should be moved to Ansible Vault or another secrets management solution.
  - Count: 2 scripts with 5 credential-related variables each

### Technical Challenges

- **Chef InSpec Integration**: Maintaining the Chef InSpec testing while standardizing on Ansible. Consider using Ansible's built-in testing capabilities or keeping InSpec as a separate testing tool.
- **Chef Automate/Infra Server Deployment**: If Chef infrastructure is still needed, creating equivalent Ansible playbooks for deployment. If not, determining what monitoring and compliance capabilities need to be replaced.

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** (high priority): Convert these Bash scripts to Ansible playbooks or determine if Chef infrastructure is still needed.
2. **website_https** and **poodle_fix** (low priority): These are already Ansible playbooks and only need minor adjustments for standardization.

### Assumptions

1. The repository is primarily used for examples and demonstrations rather than production deployments.
2. Chef InSpec is being used alongside Ansible for compliance testing, not for configuration management.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up infrastructure, not for ongoing configuration management.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing.
5. The migration goal is to standardize on Ansible while maintaining the compliance testing capabilities of Chef InSpec.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.