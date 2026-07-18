# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks for HTTPS configuration and SSL hardening with Chef InSpec tests
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration, SSL POODLE vulnerability fix, compliance testing

- **setup-automate**:
    - Description: Module containing bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification on Ubuntu 20.04. Migration considerations include replacing with Ansible-native testing solutions like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2.
- `chef-and-ansible/index.html`: Simple HTML file used for testing the web server. No migration needed.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS configuration and SSL protocols.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH security compliance.
- `setup-automate/deploy-automate.sh`: Bash script that deploys Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script that deploys Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis
  - Option 4: Consider migrating to ansible-test for unit and integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL POODLE vulnerability by enforcing TLSv1.2. This security hardening should be preserved in the migration.
  - Migration approach: Incorporate the SSL hardening directly into the main Apache configuration playbook

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This check should be preserved.
  - Migration approach: Create an Ansible assert task to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password, email)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Handler Name Mismatch**: In poodle_fix.yml, there's a mismatch between the task notification "Restart apache2" and the handler name "Restart apache". This should be fixed during migration.
  - Mitigation strategy: Standardize handler names across all playbooks

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing requires understanding the equivalent assertions.
  - Mitigation strategy: Create a mapping of InSpec resources to Ansible modules/assertions

- **Deployment Script Migration**: The Chef deployment scripts need to be converted to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef Automate and Chef Infra Server deployment

### Migration Order

1. Fix handler name mismatch in poodle_fix.yml (low risk, quick win)
2. Migrate InSpec tests to Ansible assertions or Molecule (moderate complexity)
3. Replace Test Kitchen with Molecule (moderate complexity)
4. Convert Chef deployment scripts to Ansible playbooks (higher complexity)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functioning correctly and don't need significant changes beyond the handler name fix.
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
3. There are no external dependencies or integrations beyond what's visible in the repository.
4. The Chef InSpec tests are used primarily for verification and not for continuous compliance monitoring.
5. The deployment scripts are used for setting up development/test environments and not production systems, given the hardcoded credentials.
6. The migration will maintain the same level of security compliance as the original implementation.