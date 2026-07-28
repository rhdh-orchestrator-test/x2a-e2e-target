# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, as indicated by the README in the chef-and-ansible directory.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec profile to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing framework like Molecule or maintain InSpec as a standalone testing tool
- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-based configuration management solution

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
- **SSH Security**: The InSpec profile checks for SSH root login being disabled. Ensure this security check is maintained in the migrated solution.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider using Let's Encrypt or other trusted certificate providers in production.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly but should be managed securely

### Technical Challenges

- **InSpec Integration**: Maintaining compliance testing capabilities while migrating to pure Ansible. Consider using Ansible's built-in assert module or integrating with other compliance tools.
- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality (inventory management, role-based access control, etc.)

### Migration Order

1. **website-https playbook** (already in Ansible format, low risk)
2. **poodle-fix playbook** (already in Ansible format, low risk)
3. **Chef Automate/Server setup scripts** (convert bash scripts to Ansible playbooks, moderate complexity)
4. **InSpec tests** (convert to Ansible-compatible testing framework, moderate complexity)

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The Chef components (Automate and Infra Server) are used for management and not for actual configuration of systems.
3. The InSpec tests are used to verify compliance and could be maintained separately from the Ansible playbooks.
4. The migration goal is to have a pure Ansible solution without any Chef components.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in production.
6. The self-signed certificates are for testing purposes and would be replaced with proper certificates in production.