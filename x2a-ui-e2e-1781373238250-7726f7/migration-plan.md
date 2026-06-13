# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with two main components:

1. A Chef InSpec compliance testing framework used alongside Ansible playbooks
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** as most of the Ansible components can be retained, while the Chef InSpec tests need to be converted to Ansible-native solutions. The estimated timeline for migration is **1-2 weeks** for a small team.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test page for the web server. Can be retained as-is.
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Will need to be replaced with Ansible playbooks.
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server only. Will need to be replaced with Ansible playbooks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert modules or molecule for testing
  - For complex compliance: Consider integrating with OpenSCAP or using ansible.posix.mount

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers

- **Chef Automate/Infra Server**: Replace with Ansible automation platform or AWX
  - For organizations requiring a central management platform, AWX (open-source version of Ansible Tower) can replace Chef Automate functionality

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables older protocols. This should be maintained or enhanced in the Ansible migration.
  - Migration approach: Use ansible.builtin.lineinfile or ansible.builtin.template to manage Apache SSL configuration

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained.
  - Migration approach: Use ansible.posix.sshd_config module to manage SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible.builtin.openssl_* modules with vault-encrypted private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible's assert module combined with command/shell modules to perform similar checks
  - For complex tests, consider using the community.general.xml module for parsing and validating responses

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible management
  - Mitigation: Evaluate if AWX/Tower is needed or if simple Git-based Ansible can suffice
  - Document clear procedures for teams transitioning from Chef workflow to Ansible workflow

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Retain as-is, only update to follow best practices
2. **poodle_fix.yml** (low risk, already Ansible): Retain as-is, only update to follow best practices
3. **inspec_compliance_tests** (medium complexity): Convert to Ansible assertions or molecule tests
4. **chef_deployment** (high complexity): Replace with Ansible playbooks for AWX/Tower deployment if needed

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems
3. There is no complex Chef cookbook logic that needs to be migrated
4. The deployment scripts are used for setting up Chef infrastructure, which may not be needed if fully migrating to Ansible
5. No external data sources or complex inventory management is present
6. No CI/CD pipeline integration is present that would need reconfiguration
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only