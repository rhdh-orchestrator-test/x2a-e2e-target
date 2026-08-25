# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks that are used for demonstration purposes. The repository appears to be focused on examples for technical content rather than production infrastructure code. The migration scope is relatively small, with only a few Ansible playbooks and Chef server setup scripts to consider. The estimated timeline for migration would be minimal (1-2 days) as most of the content is already in Ansible format or consists of setup scripts that may not need migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying the HTTPS website deployment
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Can be retained but configured to use only Ansible for provisioning
- **InSpec**: Can be retained for compliance testing with Ansible playbooks

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache, which should be preserved in the migration
  - Migration approach: Convert to Ansible roles with parameterized SSL configuration
- **Self-signed certificates**: The playbooks generate self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules (already in use)
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server Setup**: The bash scripts for Chef server setup would need to be replaced with equivalent Ansible roles
  - Mitigation: Create Ansible roles for setting up alternative configuration management tools if needed
- **InSpec Integration**: Maintaining the InSpec testing while migrating to pure Ansible
  - Mitigation: Keep InSpec for testing but ensure it works with the new Ansible roles

### Migration Order

1. `website_https.yml` (already in Ansible format, just needs refactoring to roles)
2. `poodle_fix.yml` (already in Ansible format, just needs refactoring to roles)
3. Chef server setup scripts (requires more significant changes)

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The InSpec tests should be preserved for compliance verification
3. The Chef server setup scripts may not need migration if the target environment will not use Chef
4. The Ansible playbooks are already in a format close to the desired end state
5. No external Chef cookbooks or complex Chef-based infrastructure is present in the repository