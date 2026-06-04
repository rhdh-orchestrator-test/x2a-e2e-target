# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Chef InSpec tests and Ansible playbooks. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting of:

1. Two Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main effort will involve converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled (STIG compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, STIG compliance check

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the existing SSL configuration in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Convert the InSpec SSH test to an Ansible assert or Molecule test.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the playbook
  - Recommend moving credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Molecule's verifier plugins or custom Ansible assert tasks.

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with Ansible Tower/AWX deployment.
  - Mitigation: Create Ansible playbooks to deploy AWX/Tower with similar user/organization structure.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Just update documentation and testing framework

2. **poodle_fix playbook** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Just update documentation and testing framework

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Server/Automate deployment scripts** (high complexity)
   - Convert to Ansible playbooks for deploying Ansible Tower/AWX
   - Create roles for user/organization management

### Assumptions

1. The primary goal is to migrate away from Chef components while preserving Ansible components.
2. The InSpec tests are critical for compliance and must be preserved in functionality.
3. The deployment scripts for Chef Server/Automate will be replaced with equivalent Ansible Tower/AWX deployment.
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs.
5. No additional Chef cookbooks or resources are present beyond what's visible in the repository.
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure credential management.
7. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be preserved as-is.