# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on using Chef InSpec for compliance testing alongside Ansible for configuration management. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Apache web server with SSL configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (with Chef InSpec tests)
    - Key Features: SSL certificate generation, virtual host configuration, website deployment

- **poodle_fix**:
    - Description: Security fix for the POODLE vulnerability in SSL/TLS
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (with Chef InSpec tests)
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible-native testing solutions.
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings. Should be migrated to Ansible-native security testing.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use Ansible assert module or custom modules
  - For compliance testing: Consider using ansible-lint, OpenSCAP with Ansible, or maintaining InSpec as a separate tool
  
- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the current configuration:
  - Disabling vulnerable SSL protocols (SSLv3)
  - Enforcing TLSv1.2
  - Proper certificate generation and management

- **SSH Security**: The SSH hardening profile must be maintained:
  - Root login restrictions
  - Compliance with security requirements (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Compliance Testing**: Finding an equivalent to InSpec in the Ansible ecosystem that provides the same level of compliance reporting and integration.
  - Mitigation: Consider using ansible-lint with custom rules, OpenSCAP integration, or maintaining InSpec as a separate tool while using Ansible for remediation.

- **Chef Automate Replacement**: Determining what will replace Chef Automate's functionality.
  - Mitigation: Consider Ansible Automation Platform or open-source alternatives like AWX for similar functionality.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Only needs migration of the InSpec tests to Ansible-native testing

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Only needs migration of the InSpec tests to Ansible-native testing

3. **Chef Automate deployment scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault
   - Determine replacement for Chef Automate functionality

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts mention they can work on cloud VMs as well.
4. The migration will maintain the same level of security compliance as the original configuration.
5. There is no complex Chef cookbook logic to migrate, as the repository primarily contains Ansible playbooks with Chef InSpec tests.
6. The team is familiar with both Chef and Ansible technologies.