# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used for testing - can be preserved as-is or included as a template in Ansible

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` or `shell` module

- **Test Kitchen (latest)**: Replace with:
  - Molecule for Ansible role testing
  - AWX/Tower for orchestrated testing in larger environments

- **Chef Automate/Chef Server**: Replace with:
  - Ansible AWX/Tower for web UI, role-based access control, and job scheduling
  - Ansible Galaxy for role sharing
  - Ansible Collections for organizing content

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Directly port the existing Ansible task to the new structure

- **SSH Hardening**: The SSH root login check needs to be converted to an Ansible-compatible test
  - Approach: Create an Ansible playbook with assert statements or use ansible-lint security checks

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Preserve the existing openssl_* module usage which is already Ansible-native

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for basic tests, consider Molecule for more complex scenarios
  - Example: The SSL protocol checks in website_https_verify.rb will need custom handlers in Ansible

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or replace with AWX/Tower deployment
  - Consider whether Chef server is still needed or if complete migration to Ansible is preferred

### Migration Order

1. **website_https_verify.rb** (high value, moderate complexity) - Convert InSpec tests to Ansible assertions
2. **ssh_profile.rb** (high value, low complexity) - Convert InSpec control to Ansible security check
3. **deploy-automate.sh and deploy-chef-server.sh** (moderate value, high complexity) - Convert to Ansible roles or replace functionality

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be preserved as-is
2. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of testing
3. The Chef server deployment scripts may be replaced entirely if Chef is no longer needed
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The repository is primarily for demonstration/educational purposes rather than production use
7. No complex data structures or state management is required beyond what's in the existing code