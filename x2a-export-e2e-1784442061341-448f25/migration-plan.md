# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on preserving the compliance testing capabilities of InSpec while moving all configuration management to Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance validation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS configuration. Will need to be replaced with Ansible-native testing or integrated with Ansible using ansible-test.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need to be replaced with Ansible-native testing or integrated with Ansible using ansible-test.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Will need to be replaced with Ansible roles for configuration management.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Will need to be replaced with Ansible roles for configuration management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks:
  - Option 1: Use ansible-test for integration testing
  - Option 2: Use Molecule for role testing
  - Option 3: Integrate with other testing frameworks like Serverspec or Testinfra
  - Option 4: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management
  - For compliance reporting, consider integrating with tools like OpenSCAP or maintaining InSpec as a standalone tool

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the Ansible migration.
  - Migration approach: Maintain the same security configurations in the Ansible roles

- **SSH Security**: The InSpec tests validate SSH security configurations (disabling root login). This compliance check should be preserved.
  - Migration approach: Create Ansible roles that enforce the same SSH security configurations and include tests to validate them

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **Compliance Testing**: The repository uses Chef InSpec for compliance testing. Ansible has less mature native testing capabilities.
  - Mitigation: Either maintain InSpec as a standalone tool called from Ansible or invest in developing equivalent tests using Ansible-native testing frameworks

- **Chef Server Deployment**: The repository includes scripts for deploying Chef Automate and Chef Infra Server, which won't be needed in an Ansible-only environment.
  - Mitigation: Replace with Ansible AWX/Tower deployment if centralized management is required

### Migration Order

1. **Ansible Playbooks** (Low risk, high value)
   - `website_https.yml` and `poodle_fix.yml` are already Ansible playbooks and can be directly reused
   - Convert these into proper Ansible roles with variables, templates, and handlers

2. **Testing Framework** (Moderate complexity)
   - Replace Test Kitchen with Molecule
   - Either integrate InSpec tests with Ansible or rewrite them using Ansible-native testing

3. **Chef Server Deployment** (High complexity)
   - Replace Chef Automate/Infra Server deployment scripts with Ansible AWX/Tower deployment if needed
   - Create Ansible roles for user and organization management

### Assumptions

1. The primary goal is to consolidate on Ansible as the configuration management tool while maintaining the same level of compliance testing.
2. The InSpec tests are valuable and should be preserved in some form, either by calling InSpec from Ansible or by rewriting them using Ansible-native testing.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which won't be needed in an Ansible-only environment.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be flexible enough to work on both on-premises and cloud VMs.
5. The hardcoded credentials in the setup scripts are for testing purposes only and should be replaced with Ansible Vault in the production environment.
6. The repository is primarily used for demonstration purposes (as indicated by the README.md) and may not represent a complete production environment.