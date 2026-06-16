# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL protocol validation, SSH configuration compliance

- **chef_automate_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page for the web server. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if deeply invested

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configurations that need to be preserved:
  - Disabling SSLv3 protocol (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - Self-signed certificate generation

- **SSH Security**: InSpec tests verify SSH root login is disabled, which should be maintained in the Ansible migration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be handled securely
  - Count of credentials detected: 3 (username, password, SSL key)

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.uri module for HTTP tests and ansible.builtin.command with openssl for SSL tests

- **Chef Automate Deployment**: The bash scripts for Chef Automate deployment will need to be completely rewritten as Ansible roles
  - Mitigation: Create dedicated Ansible roles for infrastructure components

### Migration Order

1. **website_https.yml** (already in Ansible format, just needs review and potential refactoring into roles)
2. **poodle_fix.yml** (already in Ansible format, just needs review and potential refactoring into roles)
3. **InSpec tests** (convert to Ansible assertions or Molecule tests)
4. **Chef Automate deployment scripts** (convert to Ansible roles)

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating the dependency on Chef InSpec for testing.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. The self-signed certificates are acceptable for the environment (not production).
4. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migration.
5. Test Kitchen is only used for development/testing and not for production deployments.
6. The Apache configuration requirements will remain the same in the migrated solution.
7. The SSH security requirements specified in the InSpec tests are still relevant and should be enforced.