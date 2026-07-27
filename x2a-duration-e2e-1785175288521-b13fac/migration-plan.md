# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions and updating the Chef Automate/Infra Server deployment scripts to use Ansible playbooks instead.

**Estimated timeline**: 1-2 weeks for a complete migration, with minimal complexity.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration will require updating to use Ansible-native testing solutions.
- `index.html`: Simple HTML file used for testing web server functionality. Can be kept as-is or incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions such as:
  - Ansible Molecule for integration testing
  - ansible-lint for static code analysis
  - pytest-ansible for functional testing
  - OpenSCAP or OVAL for compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-based solutions:
  - AWX (open-source version of Ansible Tower)
  - Ansible Automation Platform
  - GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. This should be preserved in the migrated Ansible playbooks.
  - Migration approach: Keep the same SSL configuration logic but refactor into Ansible roles

- **SSH Security**: The InSpec tests check for SSH root login configuration. This should be incorporated into Ansible playbooks.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use ansible.builtin.assert or ansible.builtin.command modules to implement similar checks

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible playbooks will require understanding the Chef Server architecture.
  - Mitigation: Create Ansible roles that handle the installation and configuration of equivalent functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Refactor into proper Ansible roles with better structure.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity. Convert to Ansible-native testing solutions.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity. Replace with Ansible playbooks that deploy alternative infrastructure.

### Assumptions

1. The primary goal is to move away from Chef InSpec and use Ansible-native testing solutions.
2. The existing Ansible playbooks are functional and follow best practices.
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Infra Server.
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
5. The security requirements implemented in the InSpec tests need to be preserved in the Ansible solution.
6. The deployment scripts are used for setting up development/test environments and not production systems.