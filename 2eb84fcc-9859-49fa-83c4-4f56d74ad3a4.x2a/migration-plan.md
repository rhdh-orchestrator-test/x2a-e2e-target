# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The migration will primarily involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

- **chef_deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure Apache web server with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities (POODLE) in Apache
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening that must be preserved:
  - TLS protocol restrictions (disabling SSLv3, enabling TLSv1.2)
  - Self-signed certificate generation
  - These should be maintained in the migrated Ansible roles

- **SSH Hardening**: The InSpec tests check for SSH root login restrictions:
  - Implement equivalent checks in Ansible
  - Consider adding an Ansible role for SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - These should be moved to Ansible Vault during migration

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible modules
  - Ensuring the same level of reporting and documentation

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible:
  - Will require understanding the Chef server architecture
  - May need to use the `uri` module to interact with Chef APIs
  - Will need to handle certificate and key file management

### Migration Order

1. **website_https playbook** (already in Ansible, low risk)
   - Review and optimize the existing playbook
   - Convert to an Ansible role for better reusability

2. **poodle_fix playbook** (already in Ansible, low risk)
   - Review and optimize
   - Consider merging into a comprehensive Apache security role

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible playbooks
   - Implement secret management with Ansible Vault

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining the same level of compliance verification
2. The existing Ansible playbooks are working correctly and don't need significant modifications
3. The Chef server deployment scripts are still needed (rather than being replaced by another solution)
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No additional Chef cookbooks or recipes exist beyond what's visible in the repository
6. The migration doesn't need to address scaling concerns (the examples appear to be for demonstration purposes)
7. No CI/CD integration is currently in place that would need to be updated