# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server setup. The migration scope is relatively small, focusing on:

1. Ansible playbooks for web server configuration with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main work involves converting the Chef InSpec tests to Ansible-compatible testing frameworks and updating the deployment scripts to use Ansible roles instead of shell scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Replace with Ansible-compatible testing frameworks like:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - ansible-test for module testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX (open-source version of Ansible Tower)

### Security Considerations

- **SSL Configuration**: The migration must maintain the same level of security by ensuring:
  - TLSv1.2 is enabled and older protocols are disabled
  - Self-signed certificates are properly generated
  - Apache SSL configuration is properly applied

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled, which must be maintained in the Ansible configuration

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - No encrypted data bags or Chef Vault usage detected
  - SSL certificates are generated dynamically, not stored

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-compatible testing frameworks will require mapping InSpec resources to testinfra or other testing tools
  - Mitigation: Create a mapping document for InSpec resources to testinfra/ansible-test equivalents

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles
  - Mitigation: Create an Ansible role that performs the same steps as the shell scripts, using Ansible modules for idempotency

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Only needs minor updates to follow best practices
   - Update variable handling to use Ansible Vault for sensitive data

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Only needs minor updates to follow best practices
   - Combine with website-https into a single role for Apache management

3. **InSpec tests** (moderate complexity)
   - Convert to testinfra or other Ansible-compatible testing framework
   - Ensure all compliance checks are maintained

4. **Chef Automate/Server deployment scripts** (high complexity)
   - Convert to Ansible roles
   - Use Ansible Vault for credentials
   - Consider integration with existing configuration management

### Assumptions

1. The current setup is used for testing and demonstration purposes, not production
2. The InSpec tests are used for compliance verification of Ansible-managed systems
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced with Ansible infrastructure
4. No external dependencies or integrations beyond what's visible in the repository
5. No custom Chef resources or complex Chef-specific functionality that would be difficult to replicate in Ansible
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. The migration will maintain the same level of security and compliance checking