# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution. The estimated timeline for this migration is 1-2 weeks, with low complexity.

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
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible content.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - For compliance testing: Use Ansible's built-in assert module or migrate to ansible-lint
  - For infrastructure validation: Convert InSpec tests to Ansible tasks with appropriate assertions
  - For security compliance: Consider integrating with OpenSCAP or converting InSpec controls to Ansible security roles

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solutions

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Migration approach: Preserve the same SSL protocol restrictions in the Ansible roles
  
- **SSH Hardening**: The SSH root login restriction check must be maintained
  - Migration approach: Convert the InSpec control to an Ansible task that ensures the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible validation tasks
  - Mitigation: Use Ansible's assert module and uri module to replicate the HTTP/HTTPS validation tests
  - Consider using the ansible.posix.authorized_key module for SSH configuration validation

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible management
  - Mitigation: Evaluate if Ansible AWX/Tower or other management tools are needed to replace Chef Server functionality

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - moderate complexity, requires conversion to Ansible testing
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - high complexity, requires architectural decisions

### Assumptions

1. The primary goal is to move to a pure Ansible solution without any Chef components
2. The InSpec tests are used primarily for validation and can be replaced with equivalent Ansible tasks
3. There is no complex Chef cookbook logic that needs to be migrated, as the repository mainly contains Ansible playbooks with InSpec tests
4. The deployment scripts for Chef Automate and Chef Infra Server are intended to be replaced with an Ansible-based management solution
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The security requirements and compliance standards referenced in the InSpec tests (e.g., STIG) must be maintained in the Ansible solution