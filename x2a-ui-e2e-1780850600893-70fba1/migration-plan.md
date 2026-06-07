# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

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
    - Key Features: Security hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migration.
  - Migration approach: Maintain the same security configurations in the Ansible playbooks.

- **SSH Hardening**: The InSpec test checks for SSH root login being disabled.
  - Migration approach: Convert to Ansible assert or Molecule verify step to ensure this security check remains.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated during deployment and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require different approaches for different test types:
  - For port checks: Use Ansible's `wait_for` module
  - For HTTP response validation: Use Ansible's `uri` module with assertions
  - For SSL protocol verification: May require custom modules or shell commands with assertions
  
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require:
  - Creating equivalent Ansible roles for Chef server installation
  - Handling user and organization creation through Ansible
  - Managing system requirements (sysctl settings) through Ansible

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be preserved with minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles and playbooks
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Molecule for testing

### Assumptions

1. The primary goal is to move all testing and deployment to Ansible, eliminating dependencies on Chef tools.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and can be preserved with minimal changes.
3. There's no requirement to maintain backward compatibility with Chef InSpec after migration.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in Ansible.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates.
7. The migration doesn't need to address scaling or high-availability concerns not present in the original implementation.