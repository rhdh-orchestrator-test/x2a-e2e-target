# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and Chef setup scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible AWX/Tower for web UI and API functionality
- **Chef InSpec**: Can be retained as Ansible can execute InSpec tests, or migrate to Ansible's built-in testing capabilities
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible's crypto modules or external certificate management

### Technical Challenges

- **Chef InSpec Tests**: The repository uses InSpec for compliance testing. Consider either:
  1. Keeping InSpec tests and integrating them with Ansible
  2. Migrating tests to Ansible's native testing capabilities or another tool like Molecule

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be replaced with Ansible playbooks that set up an alternative solution like AWX/Tower.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **deploy-chef-server.sh** (moderate complexity): Create Ansible playbook to replace Chef Server functionality
4. **deploy-automate.sh** (high complexity): Create Ansible playbook to deploy AWX/Tower as a replacement for Chef Automate

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, not to provide production-ready infrastructure code.
2. The Chef setup scripts are used for demonstration purposes and not for critical production environments.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. No complex Chef cookbooks or recipes are present that would require significant refactoring.
5. The migration will replace Chef Automate/Server with Ansible AWX/Tower for web UI and API functionality.
6. InSpec tests can either be retained or migrated to Ansible's native testing capabilities.
7. No external dependencies or integrations are present beyond what's visible in the repository.
8. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migrated solution.