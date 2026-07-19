# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks, and ensuring the InSpec tests are properly integrated with Ansible for compliance verification.

Estimated timeline: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible/InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations include ensuring idempotency and proper secret management for SSL certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations include ensuring this is integrated with the main Apache configuration.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing frameworks or adapting to work with pure Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Migration considerations include converting to Ansible test format or maintaining InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Migration considerations include converting to Ansible test format or maintaining InSpec integration.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for configuration management system deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for configuration management system deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management or monitoring solutions
- **Chef Infra Server**: Replace with Ansible roles for configuration management
- **InSpec**: Either maintain as a compliance testing tool alongside Ansible or replace with Ansible-native testing frameworks
- **Test Kitchen**: Replace with Ansible-native testing frameworks like Molecule

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assertions or maintain InSpec for compliance testing.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - Migration approach: Replace hardcoded credentials with Ansible Vault or external secret management solutions.

### Technical Challenges

- **InSpec Integration**: Determining whether to maintain InSpec for compliance testing or migrate to Ansible-native testing.
  - Mitigation strategy: Initially maintain InSpec integration for compliance testing while evaluating Ansible-native alternatives.

- **Chef Automate Replacement**: Identifying appropriate Ansible roles or collections to replace Chef Automate functionality.
  - Mitigation strategy: Evaluate Ansible AWX/Tower or other open-source alternatives for enterprise management capabilities.

### Migration Order

1. **chef-and-ansible/website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires decision on testing strategy)
3. **setup-automate scripts** (high complexity, requires replacement of Chef Automate and Infra Server)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.md stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The InSpec tests are intended to be run against systems configured by the Ansible playbooks, as indicated by the kitchen.yml configuration.

3. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts are designed to work on both on-premises and cloud VMs.

5. The migration goal is to consolidate all configuration into Ansible, potentially replacing Chef Automate and Infra Server with Ansible AWX/Tower or other alternatives.

6. The InSpec compliance testing is a key feature that should be maintained or replaced with equivalent functionality in the Ansible migration.