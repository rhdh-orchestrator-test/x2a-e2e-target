# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting of:

1. Two Ansible playbooks for configuring a web server with HTTPS
2. Two Chef InSpec test files for validating configurations
3. Two bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible. The main challenge will be replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need to be converted to Ansible tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Will need to be converted to Ansible tests.
- `chef-and-ansible/index.html`: Sample HTML file used in the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI, job scheduling, and inventory management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migration maintains:
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Self-signed certificate generation
  - Secure virtual host configuration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure `PermitRootLogin` is disabled
  - This test should be converted to an equivalent Ansible check

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the InSpec resource types used (port, http, ssl, sshd_config)
  - Implementing equivalent checks using Ansible's assert module or Molecule
  - Ensuring the same level of compliance validation

- **Chef Server Functionality**: If Chef Server is being used for configuration management:
  - Inventory management will need to be migrated to Ansible inventory
  - Any cookbooks not visible in this repository will need separate migration

### Migration Order

1. **website_https playbook** (already Ansible, low risk)
   - Review and optimize the existing Ansible playbook
   - Convert to an Ansible role for better organization
   - Add proper variable handling instead of inline vars

2. **poodle_fix playbook** (already Ansible, low risk)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https as a role dependency

3. **InSpec Tests** (medium complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Chef Automate/Server Deployment** (high complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Implement Ansible Vault for credential storage
   - Consider using AWX/Ansible Tower as a replacement for Chef Automate

### Assumptions

1. The repository is primarily for demonstration purposes, showing how Chef InSpec can work with Ansible, rather than a production configuration.
2. The Chef Automate and Chef Server deployment scripts are intended to be replaced entirely with Ansible-based solutions.
3. There are no additional Chef cookbooks or resources beyond what's visible in the repository.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The security compliance requirements demonstrated by the InSpec tests need to be maintained in the Ansible migration.
6. No external data sources or integrations beyond what's visible in the code.
7. The migration is intended to move completely away from Chef components, including InSpec.