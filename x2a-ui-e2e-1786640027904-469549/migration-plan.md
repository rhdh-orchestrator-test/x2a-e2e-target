# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation, rather than a full production infrastructure codebase.

The migration scope is relatively small, consisting of:
1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The estimated timeline for migration is 1-2 weeks, with low complexity since most components are already in Ansible format or are simple shell scripts that can be converted to Ansible roles.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Hostname configuration, system tuning, Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Hostname configuration, system tuning, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Static HTML file for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
  - Migration strategy: Convert InSpec tests to Ansible assert tasks or Molecule verify tests
  - Alternative: Keep InSpec as a testing tool but integrate it with Ansible CI/CD pipeline

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Migration strategy: Create equivalent Molecule scenarios for each Test Kitchen suite

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols
  - Migration approach: Maintain the same security settings in the migrated Ansible roles
  - Consider updating to include TLS 1.3 support for newer systems

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Include SSH hardening in the migrated Ansible roles
  - Add Ansible tasks to enforce the same SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Tests**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation strategy: Use Ansible assert modules or consider keeping InSpec as a testing tool integrated with Ansible

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure with Ansible alternatives
  - Mitigation strategy: Develop Ansible roles for configuration management that replace Chef server functionality, or consider AWX/Tower for enterprise features

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Convert to a proper Ansible role structure
   - Add documentation and parameterization

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Convert to a proper Ansible role structure
   - Consider merging with the website-https role as a security enhancement

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for infrastructure setup
   - Replace with AWX/Tower deployment if enterprise features are needed

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts are examples and may need customization for actual environments
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex data structures or state management that would require special handling
6. The target environment will continue to be Ubuntu-based systems
7. No specific CI/CD pipeline integration requirements
8. No specific inventory management requirements