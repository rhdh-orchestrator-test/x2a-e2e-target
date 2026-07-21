# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks with Chef InSpec tests for compliance validation
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The main effort will be in converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests for SSH root login disablement, security compliance with SRG-OS-000112

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the kitchen-ansible plugin

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The current playbooks properly configure TLSv1.2 and disable SSLv3. This security practice should be maintained in the migrated Ansible playbooks.

- **SSH Hardening**: The InSpec test checks for SSH root login disablement. This security check should be implemented in the migrated Ansible playbooks using the `ansible.posix.sshd_config` module.

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, which is acceptable for testing but should use proper certificate management in production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions to ensure equivalent coverage.
  - Mitigation: Create a test mapping document and validate each test case individually.

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible requires understanding the exact configuration needed.
  - Mitigation: Document all Chef Server configuration parameters before migration and create equivalent Ansible roles.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Only needs minor updates to follow Ansible best practices
   - Convert InSpec tests to Ansible assertions

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Only needs minor updates to follow Ansible best practices
   - Ensure idempotence in the replace module usage

3. **InSpec Test Profiles** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential management
   - Add proper error handling and idempotence

### Assumptions

1. The repository is primarily used for demonstration and testing purposes, not production deployments.
2. The InSpec tests are used for compliance validation and can be replaced with equivalent Ansible testing mechanisms.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments and can be replaced with Ansible playbooks.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. No external dependencies or integrations beyond what's visible in the repository.
6. No custom Chef cookbooks or recipes are being used beyond what's visible in the deployment scripts.
7. The migration will maintain the same level of security compliance as the original configuration.