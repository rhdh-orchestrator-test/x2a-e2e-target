# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-native testing solutions
2. Consolidating the deployment scripts for Chef Automate/Chef Server into Ansible playbooks
3. Preserving the compliance validation capabilities currently provided by InSpec

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (specifically root login settings)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts mention they can be used for "on-prem or cloud VM"

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module with appropriate checks
  - Option 2: Implement Molecule for testing Ansible roles
  - Option 3: Use the community.general.test_connection module for basic connectivity tests

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Server**: Since the purpose of this repository appears to be demonstrating InSpec with Ansible, the Chef Automate/Server deployment scripts should be converted to Ansible playbooks or removed if not relevant to the core functionality

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the migrated Ansible playbook

- **SSH Security**: The SSH security checks in ssh_profile.rb need to be preserved
  - Approach: Convert InSpec tests to Ansible assert statements or Molecule tests

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Approach: Maintain the same certificate generation logic in the migrated Ansible playbook

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password): 1 instance in each deployment script
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module with appropriate conditions to replicate InSpec tests
  - For complex tests, consider using Molecule with testinfra or other Python-based testing frameworks

- **Compliance Validation**: Ensuring the same level of compliance validation without InSpec
  - Mitigation: Document compliance requirements clearly and ensure Ansible tests cover all compliance checks

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, but should be reviewed for best practices and potential improvements

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, but should be reviewed for best practices and potential improvements

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert statements or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible playbooks if needed for the project
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as stated in the README.md.

2. The Chef Automate and Chef Server deployment scripts may not be essential to the core functionality and could potentially be removed if not needed.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

4. The security compliance requirements represented in the InSpec tests are critical and must be preserved in any migration.

5. There are no external dependencies or integrations beyond what is visible in the repository.

6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.