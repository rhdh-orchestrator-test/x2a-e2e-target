# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate to a pure Ansible solution.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - For compliance testing: Use Ansible's built-in assert module or migrate to ansible-lint
  - For infrastructure testing: Use Molecule with Testinfra or Goss
  - For security scanning: Consider OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms.
  - Mitigation strategy: Use Ansible's assert module for basic tests and integrate with tools like Testinfra or Goss for more complex infrastructure testing.

- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible Automation Platform setup.
  - Mitigation strategy: Create Ansible playbooks to deploy Ansible Automation Platform or AWX as a replacement for Chef Automate.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec Tests** (moderate complexity): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (high complexity): Create Ansible playbooks to replace Chef server deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining or improving compliance testing capabilities.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and can be reused with minimal changes.
3. There is no requirement to maintain backward compatibility with Chef InSpec.
4. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible automation for deploying Ansible Automation Platform or AWX.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The security requirements and compliance standards referenced in the InSpec tests (e.g., SRG-OS-000112) must be maintained in the Ansible implementation.
7. Test Kitchen will be replaced with Ansible Molecule or another Ansible-native testing framework.
8. The repository appears to be primarily for demonstration purposes rather than production use, based on the README description.