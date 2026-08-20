# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
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
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assert module where appropriate
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLSv1.2 and disable vulnerable protocols. This security hardening should be maintained in the migrated Ansible roles.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained and implemented in the Ansible roles.
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbooks - consider using Ansible Vault for storing private keys

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require creating equivalent functionality for:
  - System tuning (vm.max_map_count, vm.dirty_expire_centisecs)
  - Package installation and configuration
  - User and organization creation
  
- **InSpec Integration**: Maintaining the InSpec tests while migrating to Ansible will require:
  - Ensuring Ansible roles implement the same security controls being tested
  - Integrating InSpec execution into Ansible playbooks or CI/CD pipeline

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, convert to proper Ansible roles with standardized structure
2. **Chef Server Deployment Script** (deploy-chef-server.sh): Moderate complexity, create Ansible role for Chef Server deployment
3. **Chef Automate Deployment Script** (deploy-automate.sh): Higher complexity, create Ansible role for Chef Automate deployment

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."
2. The InSpec tests are intended to be maintained as they demonstrate compliance automation alongside Ansible.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
5. The Apache configuration in the Ansible playbooks is intended to demonstrate secure web server deployment rather than a specific application requirement.