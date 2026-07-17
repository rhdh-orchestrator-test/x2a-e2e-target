# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks with Chef InSpec tests for validation, along with shell scripts for deploying Chef Server and Chef Automate. The migration scope is relatively small, focusing on consolidating the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Sample HTML file for testing web server functionality. Can be preserved as-is or integrated into Ansible content structure.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Lint for static code analysis
  - Option 2: Molecule for comprehensive testing
  - Option 3: Ansible Test for integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server Deployment**: Convert bash scripts to Ansible playbooks for infrastructure deployment

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security by disabling SSLv3 and enabling only TLSv1.2. This security hardening should be preserved in the migrated solution.

- **SSH Security**: The ssh_profile.rb InSpec test verifies that SSH root login is disabled. This security check should be implemented in the Ansible-native testing solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates in website_https.yml should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks will require understanding the equivalent assertions and test structures.
  - Mitigation: Use Molecule's verifier plugins or custom Ansible tasks to perform similar validation

- **Chef Server Deployment**: The Chef Server deployment scripts contain specific Chef commands that need to be translated to Ansible tasks.
  - Mitigation: Research Ansible modules for Chef management or use command/shell modules with appropriate idempotency checks

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (higher complexity, requires conversion from bash to Ansible)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef InSpec dependencies
2. The Chef deployment scripts (deploy-automate.sh, deploy-chef-server.sh) are intended to be migrated to Ansible rather than preserved for deploying Chef infrastructure
3. Test Kitchen is used only for development/testing and not in production pipelines
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Self-signed certificates are acceptable for the HTTPS configuration (not using Let's Encrypt or commercial certificates)
6. No external inventory or variable files exist beyond what's in the repository
7. No complex role structure or variable precedence needs to be preserved