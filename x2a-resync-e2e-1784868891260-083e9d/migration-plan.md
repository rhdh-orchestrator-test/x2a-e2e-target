# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be retained) and moderate complexity for converting the InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (STIG)

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file for the web server. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise management
  - Option 2: Ansible Automation Platform
  - Option 3: Simple Git-based workflow with CI/CD integration

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. This security configuration should be preserved in the migration.
  - Migration approach: Retain the existing Ansible tasks for SSL configuration.

- **SSH Hardening**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests that verify the same security controls.

- **Self-signed Certificates**: The playbook generates self-signed certificates.
  - Migration approach: Consider enhancing with Let's Encrypt integration for production environments.

- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Molecule which provides a more structured testing framework for Ansible.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may be difficult to replicate.
  - Mitigation: Consider integrating with compliance tools like OpenSCAP or maintaining InSpec for testing only.

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management.
  - Mitigation: Document manual steps for AWX/Tower setup or create Ansible playbooks to deploy AWX/Tower.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, can be used as-is.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, convert to Ansible-compatible testing.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, replace with Ansible playbooks for infrastructure management.

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating the need for Chef components.
2. The existing Ansible playbooks are working correctly and don't require functional changes.
3. The compliance testing currently done with InSpec is still required after migration.
4. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible automation or a different management platform.
5. The target environment (Ubuntu 20.04) will remain the same after migration.
6. Test Kitchen is currently used for development and testing, and an equivalent workflow is desired in the Ansible ecosystem.
7. The security controls being tested are still relevant and should be preserved in the migration.