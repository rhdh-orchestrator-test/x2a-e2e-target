# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks that are used for demonstration purposes. The repository appears to be primarily focused on showing how Chef InSpec can be used alongside Ansible for compliance automation, rather than being a production infrastructure codebase.

The migration scope is relatively small, consisting of:
- Two Ansible playbooks for configuring a web server with HTTPS
- Two bash scripts for deploying Chef Automate and Chef Infra Server
- Chef InSpec tests for verifying configurations

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be low complexity and could be completed in 1-2 days by a single engineer.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: The repository uses InSpec for compliance testing. This can be replaced with:
  - Ansible's built-in `assert` module for basic tests
  - The `ansible-lint` tool for static analysis
  - Integration with tools like Molecule for more comprehensive testing

- **Test Kitchen**: Currently used to provision test environments. Replace with:
  - Ansible Molecule for testing roles and playbooks
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Migration should ensure:
  - Modern TLS protocols are enforced (TLS 1.2+)
  - Weak ciphers are disabled
  - Self-signed certificates are replaced with proper CA-signed certificates in production

- **SSH Hardening**: The InSpec tests check for SSH root login restrictions. Migration should:
  - Incorporate these checks into Ansible roles
  - Implement SSH hardening according to CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: The bash scripts that deploy Chef Automate and Chef Infra Server need to be replaced with:
  - Ansible roles for deploying alternative configuration management or compliance tools
  - Or Ansible roles that deploy Chef components if they must be retained

- **InSpec Tests**: The InSpec tests need to be converted to:
  - Ansible assertions
  - Molecule verify tests
  - Or integrated with another compliance tool like OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need minor refactoring to follow best practices:
   - Convert to roles for better organization
   - Use Ansible Vault for any sensitive data
   - Update to use more idempotent approaches where needed

2. **InSpec Tests**: Convert the InSpec tests to equivalent Ansible/Molecule tests:
   - website_https_verify.rb → Ansible assertions or Molecule tests
   - ssh_profile.rb → Ansible assertions or Molecule tests

3. **Chef Deployment Scripts**: Replace the bash scripts with Ansible roles:
   - deploy-automate.sh → Ansible role for configuration management setup
   - deploy-chef-server.sh → Ansible role for configuration management setup

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The InSpec tests are essential and need to be preserved in some form
3. The Chef Automate and Chef Infra Server deployments are needed for the demonstrations
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the code
6. No complex data structures or state management requirements
7. No specific performance requirements for the deployed services