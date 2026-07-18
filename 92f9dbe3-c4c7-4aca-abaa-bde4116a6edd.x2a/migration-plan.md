# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with two main components:

1. A set of Ansible playbooks with Chef InSpec tests for compliance automation
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks and converting the Chef server deployment scripts to Ansible roles.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website with SSL
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source) for smaller deployments

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve:
  - Self-signed certificate generation
  - TLS protocol security settings (disabling SSLv3, enabling TLSv1.2)
  - Apache SSL module configuration

- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain SSH hardening checks
  - Convert InSpec tests to equivalent Ansible assertions or molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in setup scripts

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use ansible.builtin.assert or community.general.assert modules for verification
  - Consider molecule for testing infrastructure

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible management
  - Mitigation: Document transition plan from Chef to Ansible for existing Chef users
  - Consider AWX/Ansible Automation Platform deployment playbooks

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Standardize existing playbooks to follow best practices
   - Update SSL configuration to use more modern approaches
   - Add proper documentation

2. **InSpec Tests** (Moderate complexity)
   - Convert to Ansible assertions or molecule tests
   - Ensure compliance checks are maintained

3. **Chef Server Deployment Scripts** (Higher complexity)
   - Convert bash scripts to Ansible roles for server deployment
   - Implement Ansible Vault for credential management
   - Create documentation for transitioning from Chef to Ansible

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. Users will be transitioning from Chef to Ansible completely, not maintaining both systems
3. The InSpec tests are essential for compliance requirements and need equivalent functionality in Ansible
4. The hardcoded credentials in setup scripts are for demonstration only and will be replaced with proper secret management
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The SSL configuration requirements (TLS 1.2, disabled SSLv3) must be maintained for security compliance
7. The Apache web server configuration will remain similar in the migrated solution