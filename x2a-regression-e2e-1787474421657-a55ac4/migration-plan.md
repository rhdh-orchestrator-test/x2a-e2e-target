# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

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
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `inspec` Ansible module

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use)

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture.
  - Mitigation: Create an Ansible role that performs equivalent setup steps, using the official Chef Automate documentation as reference

- **InSpec Integration**: Maintaining InSpec testing while moving to an Ansible-only workflow.
  - Mitigation: Use the Ansible `inspec` module to run InSpec tests as part of Ansible playbooks

### Migration Order

1. **Existing Ansible Playbooks** (low risk, already Ansible)
   - Refactor `website_https.yml` and `poodle_fix.yml` to follow Ansible best practices
   - Convert inline templates to separate template files
   - Implement variable files instead of inline variables

2. **Test Infrastructure** (moderate complexity)
   - Migrate Test Kitchen configuration to Ansible Molecule
   - Maintain InSpec tests but integrate them with Ansible workflow

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, based on the README stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The InSpec tests are intended to be maintained and used with Ansible, as the repository already demonstrates Chef InSpec with Ansible integration.

3. The Chef Automate and Chef Server deployment scripts are intended to be migrated to Ansible rather than maintained as-is.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.

5. The target environment is Ubuntu 20.04 based on the Test Kitchen configuration, though the deployment scripts don't specify an OS.

6. The migration will maintain compatibility with Vagrant for local testing.