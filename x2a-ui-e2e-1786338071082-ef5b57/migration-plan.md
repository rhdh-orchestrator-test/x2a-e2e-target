# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef setup scripts and Ansible playbooks that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and Chef setup scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings
- `index.html`: Simple HTML file used as a test page

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Can be retained for compliance testing alongside Ansible or replaced with Ansible-native solutions like ansible-lint

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. This security check should be maintained in the Ansible migration.
- **Credentials Management**: The setup scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username/password in deploy-automate.sh and deploy-chef-server.sh
  - Consider using Ansible Vault for storing these credentials

### Technical Challenges

- **InSpec Integration**: The repository demonstrates InSpec with Ansible. The migration should maintain this compliance testing capability, either by continuing to use InSpec or by implementing equivalent functionality with Ansible tools.
- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible roles/playbooks. This may require research into Chef server architecture to ensure proper migration.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **deploy-chef-server.sh** (moderate complexity): Convert to Ansible role for deploying configuration management
4. **deploy-automate.sh** (moderate complexity): Convert to Ansible role for deploying Chef Automate or replace with Ansible AWX/Tower

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The InSpec tests are intended to be run against systems managed by either Chef or Ansible.
3. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
4. The deployment scripts are intended for on-premises or cloud VMs.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
6. The repository is meant to showcase how Chef InSpec can work alongside Ansible rather than being a production codebase.
7. No external dependencies or complex infrastructure are required beyond what's explicitly defined in the repository.