# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks**. The primary focus will be on:
- Preserving the InSpec compliance tests while integrating them into an Ansible-native workflow
- Converting the Chef Automate/Infra Server deployment scripts to Ansible playbooks
- Ensuring the existing Ansible playbooks follow best practices

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Continue using InSpec but integrate with Ansible using the `community.general.inspec` module
  - Option 2: Replace with Ansible's built-in `assert` module for basic tests
  - Option 3: Use `ansible-lint` for static analysis of security practices

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collections testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL/TLS configurations

- **SSH Security**: The InSpec SSH profile tests for root login restrictions
  - Approach: Create an Ansible role that applies SSH hardening and includes post-configuration verification

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Integration**: Ensuring InSpec tests continue to work with Ansible-only deployments
  - Mitigation: Create an Ansible role that installs InSpec and runs the tests as part of the playbook execution

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities
  - Mitigation: Evaluate AWX/Tower compliance reporting or integrate with third-party compliance tools

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Convert to a proper role structure

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate into the Apache role created for website-https
   - Add idempotency checks

3. **InSpec tests** (medium complexity)
   - Create Ansible integration for running the existing tests
   - Document the process for writing new compliance tests

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement Ansible Vault for credential storage

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
3. There is no requirement to maintain backward compatibility with Chef Automate/Infra Server
4. The security compliance requirements (SSH configuration, SSL/TLS settings) must be preserved in the migration
5. The self-signed certificates approach is acceptable for the migrated solution
6. No external dependencies or integrations beyond what's visible in the repository need to be considered