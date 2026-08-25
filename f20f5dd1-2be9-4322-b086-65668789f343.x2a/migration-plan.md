# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance validation. The repository also includes setup scripts for Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format. The main migration effort will involve converting the Chef InSpec tests to Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: Disables SSLv3 and enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used for testing. Migration consideration: Can be used as-is or converted to a template.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static code analysis
  - Option 4: Consider OpenSCAP integration for compliance scanning

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Use Ansible's openssl_* modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests check for SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or use ansible-lint rules.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation strategy: Use Ansible's assert module for basic tests, and consider Molecule for more complex testing scenarios.

- **Chef Automate Setup**: Converting Chef Automate setup scripts to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef server setup if still needed, or replace with Ansible AWX/Tower for similar functionality.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing)
4. **Setup Scripts** (high complexity, requires full conversion to Ansible playbooks)

### Assumptions

1. The primary goal is to consolidate all automation to Ansible, eliminating the need for Chef InSpec.
2. The Chef Automate and Chef Infra Server setup scripts may be obsolete after migration, as these would be replaced by Ansible Tower/AWX.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. Vagrant will continue to be used for development/testing environments.
5. The security compliance requirements represented in the InSpec tests need to be maintained in the Ansible solution.