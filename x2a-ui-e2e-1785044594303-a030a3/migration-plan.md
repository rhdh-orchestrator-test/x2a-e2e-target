# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Preserving the InSpec compliance testing functionality within the Ansible ecosystem

Given the limited scope (2 Ansible playbooks and 2 Chef deployment scripts), this migration is estimated to be a low-complexity effort that could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a single node
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a single node
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test profile for verifying SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec Tests**: Maintain InSpec tests but integrate with Ansible using the ansible_inspec module or Molecule's verifier
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or maintain as a separate system managed by Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols. This security hardening should be preserved in the migrated Ansible roles.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. This should be implemented in the migrated Ansible roles.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely in the migrated solution

### Technical Challenges

- **InSpec Integration**: Ensuring that the InSpec compliance testing remains functional within an Ansible-only workflow
- **Chef Automate Replacement**: Determining if Chef Automate functionality needs to be replaced with Ansible Automation Platform or another solution
- **Testing Framework**: Migrating from Test Kitchen to Molecule while preserving test coverage

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Update to use Ansible Vault for any sensitive data
   - Integrate with Molecule for testing

2. **poodle_fix.yml** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Consider merging with website_https role as a security enhancement option

3. **Chef Deployment Scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Use Ansible Vault for credentials
   - Implement idempotent deployment logic

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content
2. The InSpec tests are essential and must be preserved in the migrated solution
3. The Chef deployment scripts are used for setting up Chef infrastructure, not for managing application configurations
4. No external dependencies or integrations beyond what's visible in the repository
5. No CI/CD pipeline integration is currently in place
6. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing
7. The migration goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment