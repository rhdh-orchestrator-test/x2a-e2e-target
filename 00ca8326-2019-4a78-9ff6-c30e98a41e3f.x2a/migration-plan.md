# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be on showing how Chef InSpec can be used alongside Ansible for compliance testing rather than containing actual Chef cookbooks for configuration management. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format or consists of InSpec tests that can be maintained as-is or converted to Ansible's built-in testing capabilities. The estimated timeline for migration would be 1-2 days of work for a single engineer.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks and InSpec tests for demonstrating compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS setup, SSL security configuration, compliance testing

- **tests**:
    - Description: Directory containing Chef InSpec tests for compliance verification
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSH security compliance checks

- **setup-automate**:
    - Description: Scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef infrastructure deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH security configuration.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing capabilities or maintain InSpec tests separately
  - Migration strategy: Convert InSpec tests to Ansible assert modules or use the ansible.builtin.shell module to run InSpec tests
  - Alternative: Use Ansible Molecule for testing, which can incorporate various verifiers

- **Test Kitchen**: Replace with Ansible Molecule for testing
  - Migration strategy: Create equivalent Molecule configuration for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols
  - Migration approach: Maintain the same security settings in the migrated Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert to Ansible assert or maintain as InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions
  - Mitigation strategy: Use Ansible's assert module for simple tests, consider maintaining InSpec for complex compliance tests or migrate to Ansible Molecule

- **Chef Server Deployment**: The bash scripts for Chef Server deployment will need to be completely rewritten
  - Mitigation strategy: Create Ansible roles for infrastructure deployment that replace the Chef Server functionality

### Migration Order

1. Ansible playbooks in chef-and-ansible directory - Low risk as they are already in Ansible format
2. InSpec tests in chef-and-ansible/tests directory - Moderate complexity to convert to Ansible assertions
3. Chef deployment scripts in setup-automate directory - High complexity, requires complete rewrite

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing.
2. The InSpec tests are intended to be run against systems configured by Ansible.
3. There are no actual Chef cookbooks for configuration management in this repository.
4. The deployment scripts are used for setting up a Chef infrastructure, which may not be needed if fully migrating to Ansible.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. No external dependencies or complex configurations are present beyond what's visible in the repository.
7. The migration will maintain the same security posture and compliance checks.