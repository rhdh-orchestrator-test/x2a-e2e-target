# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

**Timeline Estimate**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, as it's already compatible with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain with Ansible provisioner
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same server setup

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or enhance this security practice.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration should ensure this security control is maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates generated in the website_https.yml playbook
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture and configuration. The Ansible playbook will need to:
  1. Download and install Chef Automate packages
  2. Configure system requirements (sysctl settings)
  3. Create users and organizations
  4. Set up proper authentication

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible playbooks. This may require:
  1. Updating Test Kitchen configuration or migrating to Molecule
  2. Ensuring InSpec tests are properly triggered after Ansible runs

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor website_https.yml and poodle_fix.yml to follow Ansible best practices
   - Update variable handling and implement Ansible Vault for secrets

2. **Chef Automate Deployment Scripts** (Moderate complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement idempotent deployment logic

3. **Testing Framework** (Low complexity)
   - Migrate from Test Kitchen to Molecule or update Test Kitchen configuration
   - Ensure InSpec tests continue to function with migrated playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Chef InSpec tests are intended to be maintained as they demonstrate compliance automation alongside Ansible.

3. The Chef Automate and Chef Infra Server deployment scripts are intended to be converted to Ansible playbooks rather than maintained as-is.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with Ansible Vault in a production environment.

5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.

6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already well-structured and may only need minor refactoring to follow Ansible best practices.