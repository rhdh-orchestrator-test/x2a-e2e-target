# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` module

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible playbook
  
- **SSH Security**: The SSH root login check must be preserved
  - Approach: Convert the InSpec control to an Ansible assert or use ansible-lint security checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated dynamically, no migration needed for certificate storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation: Use Ansible's assert module for basic tests, or integrate with Molecule for more comprehensive testing
  
- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment, or consider if Chef server is still needed after migration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing frameworks
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires creating equivalent Ansible roles or determining if these components are still needed

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and only need minor updates for best practices.
3. The Chef InSpec tests need to be converted to Ansible-compatible testing frameworks.
4. The Chef Automate and Chef Infra Server deployment scripts may not be needed after migration if the goal is to use Ansible exclusively.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with Ansible Vault in the production environment.
6. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.