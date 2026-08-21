# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity. The repository appears to be primarily educational/demonstration content rather than production infrastructure code.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH root login security compliance
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-lint for static code analysis
  - Option 3: Maintain InSpec as a standalone testing tool that works with Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and management
  - Ansible Content Collections for configuration management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - TLSv1.2 enforcement (disabling older protocols)
  - Proper file permissions for certificates (mode 0640)

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain SSH hardening checks
  - Convert InSpec tests to equivalent Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Use Ansible assert modules or Molecule verifiers to replicate test functionality

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management:
  - Challenge: Chef Server provides organization and user management features
  - Mitigation: Implement equivalent functionality using AWX/Ansible Tower or other Ansible management tools

### Migration Order

1. **website_https.yml** (Priority 1): Already an Ansible playbook, requires minimal changes
2. **poodle_fix.yml** (Priority 1): Already an Ansible playbook, requires minimal changes
3. **InSpec Tests** (Priority 2): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles for deploying alternative management platforms

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production infrastructure
2. The existing Ansible playbooks are functional and follow best practices
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The deployment scripts are intended for single-server installations rather than distributed architectures