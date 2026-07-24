# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Technologies**: Chef InSpec, Ansible Playbooks, Bash scripts for Chef server deployment

## Module Migration Plan

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled (security compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, CCI compliance checks

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server (without Automate)
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used for testing web server functionality

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
  - Migration strategy: Convert InSpec tests to Ansible assert tasks or Molecule verify tests
  - For compliance testing, consider using ansible-lint with custom rules

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Migration strategy: Create equivalent Molecule scenarios for each Test Kitchen suite

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX
  - Migration strategy: Create Ansible playbooks to deploy and configure AWX/Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already done in the existing playbooks

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Convert InSpec SSH tests to Ansible assert tasks or use ansible-lint custom rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded usernames and passwords
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation strategy: Use Ansible's assert module for basic tests, and consider Molecule for more complex testing scenarios

- **Compliance Reporting**: Chef InSpec provides compliance reporting that needs to be replicated
  - Mitigation strategy: Integrate with Ansible Automation Platform compliance features or use a third-party compliance tool

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Only need minor adjustments to follow Ansible best practices and role structure

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure compliance reporting capabilities are maintained

3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity
   - Create Ansible playbooks to deploy and configure AWX or Ansible Automation Platform
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to migrate to a pure Ansible solution, eliminating dependencies on Chef products
2. Compliance testing and reporting are important aspects that need to be maintained
3. The existing Ansible playbooks follow older conventions and would benefit from being restructured as roles
4. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible Automation Platform or AWX deployment
5. The Test Kitchen testing framework will be replaced with Molecule
6. The target environment will remain Ubuntu 20.04 on Vagrant VMs
7. No external Chef cookbooks or complex Chef-specific features are in use that would require special migration handling