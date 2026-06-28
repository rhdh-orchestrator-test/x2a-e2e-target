# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH configuration compliance checks

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-specific testing framework configuration
- `index.html`: Sample HTML file used for testing - can be preserved as-is or included as a template in Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Ansible's assert module for basic compliance checks
  - Option 3: Integration with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for enterprise management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) with proper certificate management

- **SSH Security Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert to Ansible assert tests or Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of test assertions.
  - Mitigation: Use Ansible's built-in modules like `assert`, `fail`, and `uri` to replicate InSpec tests, or integrate with Molecule for more comprehensive testing.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible requires understanding of Chef server architecture.
  - Mitigation: Create Ansible roles that handle the installation and configuration of equivalent CI/CD and configuration management tools like AWX/Tower.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - No actual migration needed

2. **poodle_fix playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - No actual migration needed

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible Molecule tests or assert statements
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for deploying alternative solutions like AWX/Tower
   - Ensure user/organization management is handled properly

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need significant changes.
2. The organization is moving completely away from Chef and wants to standardize on Ansible.
3. There's a need to replace Chef Automate/Infra Server functionality with equivalent Ansible-based solutions.
4. The InSpec tests need to be converted to maintain the same level of compliance checking.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. The self-signed certificates are acceptable for the use case, rather than requiring integration with a certificate authority.