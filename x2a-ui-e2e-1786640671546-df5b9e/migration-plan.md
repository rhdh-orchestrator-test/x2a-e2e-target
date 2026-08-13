# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for validating the configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Continue using InSpec but integrate with Ansible via ansible_inspec collection
  - Option 2: Migrate to ansible-lint and ansible-test for compliance testing
  - Option 3: Use pytest-ansible for more comprehensive testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable vulnerable protocols
  - Migration approach: Maintain the same security settings but update to modern Ansible modules and best practices
  - Consider adding TLS 1.3 support in the migrated version

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint security rules

- **Credential Management**: 
  - Hardcoded credentials in deploy scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1: InSpec Test Migration**: 
  - Description: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation strategy: Use ansible.builtin.assert module or ansible-test framework to create equivalent tests

- **Challenge 2: Chef Automate/Server Deployment**: 
  - Description: Replacing Chef Automate/Server deployment scripts with Ansible roles
  - Mitigation strategy: Create Ansible roles that perform equivalent setup or consider if Chef Automate/Server is still needed

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Update to use modern Ansible modules and best practices
   - Add idempotency improvements

2. **poodle-fix playbook** (low risk, already Ansible)
   - Update to use modern Ansible modules and best practices
   - Consolidate with website-https playbook if appropriate

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles for Chef Automate/Server deployment
   - Or evaluate if this functionality is still needed

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The InSpec tests are essential and need to be preserved in some form
3. The deployment of Chef Automate/Server is still a requirement (if not, these scripts could be deprecated)
4. The target environment will continue to be Ubuntu 20.04 or newer
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the codebase
7. No specific performance requirements for the Apache web server configuration
8. Self-signed certificates are acceptable (no need for Let's Encrypt or commercial certificates)