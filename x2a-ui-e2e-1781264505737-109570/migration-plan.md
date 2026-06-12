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
    - Key Features: Security hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for Python-based testing
  - Option 2: Ansible Test for native Ansible testing capabilities
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source version of Ansible Tower)
  - Ansible Semaphore
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables vulnerable SSL protocols.
  - Migration approach: Maintain the same configuration in the Ansible playbooks.

- **SSH Hardening**: The SSH security compliance checks in ssh_profile.rb need to be preserved.
  - Migration approach: Convert to Ansible assert tasks or Molecule/Testinfra tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - Self-signed certificates are generated on the fly; consider using ansible-vault for storing pre-generated certificates.
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks requires understanding both testing paradigms.
  - Mitigation: Use Molecule with Testinfra which provides similar functionality to InSpec but is compatible with Ansible workflows.

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible requires understanding Chef's architecture.
  - Mitigation: Create Ansible roles that replicate the functionality of Chef Automate/Server or deploy alternative solutions like AWX.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need to be organized into proper roles and potentially refactored for best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requiring conversion to Ansible-compatible testing frameworks.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requiring complete rewrite as Ansible playbooks and potentially architectural changes.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes beyond organization into proper roles.

2. The Chef InSpec tests are used primarily for validation and compliance checking, not for configuration management.

3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible playbooks that either deploy similar tools (like AWX) or implement the same functionality directly.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. The migration will maintain the same level of security compliance as the original implementation.

6. No external data sources or integrations beyond what's visible in the repository are required for the functionality.