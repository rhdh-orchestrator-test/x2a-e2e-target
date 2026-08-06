# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the Chef InSpec tests for compliance validation

The migration complexity is **LOW** as most of the repository already uses Ansible with InSpec for testing. The estimated timeline for migration is **1-2 weeks** for a single developer, primarily focused on converting the bash deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile to verify SSH security configuration
- `chef-and-ansible/index.html`: Static HTML file for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as-is for compliance testing, as it's compatible with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible playbooks
- **kitchen-ansible**: Replace with Ansible Molecule for testing Ansible playbooks
- **Vagrant**: Can be maintained for local testing or replaced with containerized testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLSv1.2 and disable vulnerable protocols
  - Migration approach: Maintain the same security settings in the Ansible playbooks
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Ensure SSH hardening is included in the Ansible playbooks

- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Consider using Ansible's `community.crypto` collection for certificate management

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Use Ansible Vault to secure credentials

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef Automate and Chef Infra Server deployment
  - Use Ansible's `command` or `shell` modules to execute the Chef Automate CLI commands
  - Use Ansible's `template` module to generate configuration files

- **InSpec Integration**: Maintaining InSpec tests with Ansible
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests
  - Alternatively, use Ansible Molecule with InSpec verifier

### Migration Order

1. **website_https playbook** (already in Ansible, low risk)
   - Review and optimize the existing playbook
   - Convert to Ansible role structure for better organization

2. **poodle_fix playbook** (already in Ansible, low risk)
   - Review and optimize the existing playbook
   - Consider merging with website_https as a security enhancement role

3. **chef-server-deploy script** (moderate complexity)
   - Convert to Ansible playbook
   - Use Ansible Vault for credentials
   - Create idempotent tasks for Chef Server installation

4. **chef-automate-deploy script** (moderate complexity)
   - Convert to Ansible playbook
   - Use Ansible Vault for credentials
   - Create idempotent tasks for Chef Automate installation

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are intended to be maintained as part of the compliance automation strategy
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The Apache configuration is intended to be secure by default with TLSv1.2
6. The Chef Automate and Chef Infra Server deployment scripts are intended to be run on a fresh Ubuntu installation
7. The migration will maintain compatibility with existing InSpec tests