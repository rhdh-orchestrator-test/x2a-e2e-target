# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef setup scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with some Chef server setup scripts. The migration complexity is relatively low as most of the content is already in Ansible format, with only the Chef server deployment scripts needing conversion. Estimated timeline for migration is 1-2 weeks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test profile for verifying SSH security configuration
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule with testinfra, or maintain InSpec as a standalone testing tool
- **Test Kitchen**: Replace with Ansible-native testing solutions like Molecule
- **Chef Automate/Server**: Replace with Ansible AWX/Tower or other Ansible-compatible configuration management platforms

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH security checks in ssh_profile.rb should be implemented in Ansible
- **Self-signed Certificates**: The certificate generation process should be maintained or improved in the Ansible migration
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Testing**: Deciding whether to maintain InSpec for testing or migrate to Ansible-native testing tools
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks
- **Compliance Automation**: Ensuring that the compliance automation capabilities of InSpec are maintained in the Ansible migration

### Migration Order

1. website_https.yml (already in Ansible format, low risk)
2. poodle_fix.yml (already in Ansible format, low risk)
3. InSpec tests conversion to Ansible-compatible testing framework (moderate complexity)
4. Chef server deployment scripts conversion to Ansible playbooks (high complexity)

### Assumptions

1. The repository is primarily a demonstration of how Chef InSpec can be used with Ansible, rather than a production environment
2. The Chef server deployment scripts are intended for setting up a test environment
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
4. The migration will maintain the same level of security hardening and compliance testing
5. The InSpec tests are considered valuable and should be preserved in some form
6. No actual Chef cookbooks or recipes need migration as none were found in the repository