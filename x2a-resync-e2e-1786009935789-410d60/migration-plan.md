# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks into a more structured Ansible project
3. Converting Chef Automate and Chef Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of low complexity and could be completed within 1-2 weeks.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec tests to verify HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing Test Kitchen with Ansible-native testing frameworks.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks such as:
  - Molecule for Ansible role testing
  - ansible-lint for static code analysis
  - testinfra for infrastructure testing (Python-based alternative to InSpec)

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can either:
  - Install and configure alternative compliance tools like OpenSCAP
  - Or maintain Chef InSpec as a standalone tool without Chef Server/Automate

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert to an Ansible role with appropriate handlers and idempotent tasks

- **SSH Security**: The SSH compliance checks need to be maintained
  - Migration approach: Convert InSpec tests to testinfra or implement as Ansible pre/post tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password, email)
  - Migration approach: Use Ansible Vault to secure credentials

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to an Ansible-compatible testing framework
  - Mitigation: Map InSpec resources to equivalent testinfra or Molecule verifiers
  - Example: InSpec's `describe port(443)` can be replaced with testinfra's `host.socket("tcp://0.0.0.0:443")`

- **Maintaining Compliance Checks**: Ensuring all compliance checks are preserved during migration
  - Mitigation: Create a compliance matrix mapping InSpec tests to their Ansible/testinfra equivalents

- **Self-Signed Certificate Generation**: Ensuring the certificate generation process is properly migrated
  - Mitigation: Use Ansible's `openssl_*` modules (already in use in the existing playbooks)

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Restructure as an Ansible role with proper variables and templates
   - Implement idempotence improvements

2. **poodle_fix.yml** (low risk, already Ansible)
   - Convert to an Ansible role or include in the website_https role
   - Improve handler naming consistency

3. **InSpec Tests** (moderate complexity)
   - Convert to testinfra or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a complete production environment
2. The InSpec tests are intended to work with the Ansible playbooks rather than with Chef cookbooks
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced in production
5. The migration aims to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
6. The Chef Automate and Chef Server deployment might be replaced with alternative compliance tools or a standalone InSpec installation