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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance tagging (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed as it's a static content file.

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

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain the TLSv1.2 protocol restriction
  - Ensure proper certificate generation and management

- **SSH Security**: The SSH root login compliance check needs to be preserved
  - Convert the InSpec control to equivalent Ansible assertions or Molecule tests
  - Maintain compliance metadata (STIG IDs, CCI references)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing style to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with well-structured test tasks
  - Consider using community.general.test_module for more test capabilities

- **Compliance Metadata**: Preserving compliance metadata (STIG IDs, CCI references) in Ansible
  - Mitigation: Use task/play tags and documentation in YAML comments
  - Consider generating compliance reports using custom Ansible modules or callbacks

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or replace with alternative configuration management solutions

### Migration Order

1. **website_https.yml** (already Ansible, no migration needed)
2. **poodle_fix.yml** (already Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible assertions or Molecule tests)
4. **ssh_profile.rb** (convert InSpec compliance control to Ansible assertions with appropriate tags)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible playbooks or consider alternative solutions)

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The Chef Automate and Chef Infra Server deployment scripts are still needed (rather than being replaced entirely)
3. The compliance requirements (STIG, CCI) are still relevant and need to be preserved
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No additional functionality beyond what exists in the current repository is required
6. The self-signed certificates are acceptable for the environment (no need for proper CA-signed certificates)
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution