# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing. Migration consideration: Keep as-is or incorporate into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to Ansible assert tasks
  - Option 3: Maintain InSpec as a separate testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the SSL configuration parameters in the Ansible tasks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec SSH tests to Ansible assert tasks or testinfra tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible Vault for storing pre-generated certificates

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions may require additional work.
  - Mitigation strategy: Use Ansible's assert module or testinfra to replicate InSpec tests.

- **Chef Automate Deployment**: The bash scripts for Chef Automate deployment need to be converted to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef Automate and Chef Server deployment, using variables instead of hardcoded values.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Automate deployment scripts** (higher complexity, requires full conversion from bash to Ansible)

### Assumptions

1. The primary goal is to migrate all components to pure Ansible without any Chef dependencies.
2. The InSpec tests need to be converted to Ansible-native testing solutions rather than kept as InSpec.
3. The repository is primarily for demonstration purposes and not a production system.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migrated solution.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The self-signed certificate generation approach is acceptable for the migrated solution.
7. The migration will maintain the same level of security compliance checking currently provided by InSpec.