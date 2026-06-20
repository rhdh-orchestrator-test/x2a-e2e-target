# MIGRATION FROM CHEF AND BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks, along with Bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks (already in the target format)
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Converting Bash deployment scripts for Chef infrastructure to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that part of the codebase is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Bash scripts that need individual migration planning:

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

- **inspec_website_tests**:
    - Description: Chef InSpec tests for validating HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL protocol security verification

- **inspec_ssh_profile**:
    - Description: Chef InSpec security profile for SSH configuration validation
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool that can work alongside Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or adapt existing kitchen.yml to work with Ansible-only workflow

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook addresses SSL POODLE vulnerability by enforcing TLSv1.2. This security hardening should be preserved in the migration.
  
- **SSH Security**: The ssh_profile.rb InSpec test enforces SSH root login restrictions according to STIG compliance requirements. This check should be converted to an Ansible-compatible test.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require additional tooling or custom development. The security metadata (STIG IDs, CCI numbers) in the SSH profile should be preserved.
  - Mitigation: Consider using ansible-test or custom modules to implement similar functionality

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks while maintaining the same functionality.
  - Mitigation: Create Ansible roles for Chef server deployment that replicate the bash script functionality

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in target format
   - Review and optimize according to Ansible best practices
   - Update any deprecated syntax or modules

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible-compatible testing framework
   - Ensure all security checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The repository is primarily used for demonstration purposes as indicated by the main README.md
3. The InSpec tests are used for validation and compliance checking rather than for configuration management
4. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely with Ansible in the final migration
5. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
6. No external dependencies or integrations beyond what's visible in the repository
7. No CI/CD pipeline integration is currently implemented that would need to be updated