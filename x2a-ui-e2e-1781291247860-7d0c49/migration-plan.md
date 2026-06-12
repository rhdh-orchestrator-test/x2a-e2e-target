# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains straightforward Ansible playbooks and InSpec tests with clear purposes.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server deployment. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Maintain the same SSL configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec tests validate SSH security configurations.
  - Migration approach: Convert the SSH security tests to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated during deployment and don't require pre-existing secrets

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require understanding the testing frameworks' differences.
  - Mitigation: Use Ansible's assert module for simple tests and Molecule with Testinfra for more complex validations.

- **Chef Automate/Server Deployment**: Converting the Chef server deployment scripts to Ansible will require understanding the Chef server installation process.
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts, using Ansible's package, command, and template modules.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - These are already Ansible playbooks and require minimal changes
   - Consolidate into a single playbook with optional tags for POODLE remediation

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assert tasks or Molecule tests
   - Convert ssh_profile.rb to Ansible assert tasks or Molecule tests

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement proper secret management using Ansible Vault

### Assumptions

1. The current implementation uses Chef InSpec only for testing, not for configuration management
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The self-signed certificates approach is acceptable for the migrated solution
4. The Chef Automate and Chef Server deployment scripts are used for setting up test environments and not production systems
5. No external Chef cookbooks or complex Chef-specific features are being used
6. The migration will not require changes to the underlying application architecture
7. The hardcoded credentials in the deployment scripts are for testing purposes only