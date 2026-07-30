# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks that are used for demonstration purposes, particularly for showing how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and Chef setup scripts to migrate. The estimated timeline for migration is 1-2 days given the limited scope and straightforward nature of the configurations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks like Molecule for infrastructure testing and compliance verification
- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Evaluate if these components are needed or can be replaced with Ansible Tower/AWX for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure proper SSL settings are maintained during migration.
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure these security checks are maintained.
- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider implementing proper certificate management.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - No encrypted secrets management currently implemented

### Technical Challenges

- **InSpec Testing**: The repository relies on InSpec for compliance testing. Need to find an equivalent solution in the Ansible ecosystem (Ansible Lint, Molecule).
- **Chef Automate Integration**: If Chef Automate is being used for compliance reporting, need to find an alternative solution within the Ansible ecosystem.

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
2. **poodle_fix.yml** (low risk, already Ansible)
3. **Chef setup scripts** (moderate complexity, requires replacing with Ansible Tower/AWX setup or equivalent)
4. **Testing framework** (high complexity, requires replacing InSpec with Ansible-native testing solutions)

### Assumptions

1. The repository appears to be primarily for demonstration purposes rather than production use, based on the README and structure.
2. The Chef components (Automate and Infra Server) are used for demonstration and may not be required in the final Ansible implementation.
3. The InSpec tests are used to demonstrate compliance automation alongside Ansible and may need to be replaced with equivalent functionality.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and would need proper secret management in a production environment.
5. The Ansible playbooks are already well-structured and would require minimal changes to conform to best practices.
6. The migration target is likely to be a pure Ansible environment, possibly with Ansible Tower/AWX for centralized management.