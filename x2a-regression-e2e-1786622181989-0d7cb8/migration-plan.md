# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already using Ansible.

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen with Ansible**: Maintain but update to use pure Ansible testing frameworks like Molecule
- **InSpec**: Maintain as is for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance these security controls:
  - Self-signed certificate generation
  - Disabling of insecure protocols (SSLv3)
  - Enabling of secure protocols (TLSv1.2)

- **SSH Hardening**: InSpec tests verify SSH security configurations. Migration should ensure:
  - Root login remains disabled
  - SSH security controls are maintained

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password)

### Technical Challenges

- **Chef Automate/Infra Server Deployment**: Converting the Chef deployment scripts to Ansible requires:
  - Creating Ansible roles for Chef Automate and Chef Infra Server installation
  - Implementing idempotent configuration management
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)

- **InSpec Integration**: Ensuring continued integration between Ansible and InSpec for compliance testing:
  - Maintaining the compliance-as-code workflow
  - Ensuring InSpec tests run correctly after Ansible provisioning

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already Ansible)
   - Refactor `website_https.yml` and `poodle_fix.yml` to follow Ansible best practices
   - Convert inline templates to separate template files
   - Implement variable files for better parameterization

2. **Chef Deployment Scripts** (Medium complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement variable files to replace hardcoded values
   - Use Ansible Vault for sensitive information

3. **Testing Framework** (Low complexity)
   - Update Test Kitchen configuration or migrate to Molecule
   - Maintain InSpec tests for compliance validation

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md
2. The Chef deployment scripts are used for setting up Chef infrastructure, not for actual configuration management
3. InSpec is the preferred tool for compliance testing and will be maintained
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes are present that require migration
6. The existing Ansible playbooks are functional and only need refactoring, not complete rewriting
7. No external dependencies or complex infrastructure are required beyond what's visible in the repository