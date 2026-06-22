# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol verification, SSH configuration verification

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen (latest)**: Replace with Molecule for Ansible-native testing

- **Vagrant (latest)**: Can be retained as a development/testing platform or replaced with other virtualization solutions compatible with Molecule

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Ensure the Ansible playbook continues to enforce the same SSL/TLS protocol restrictions

- **SSH Security Settings**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Implement equivalent checks using Ansible's assert module or Molecule

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests and Molecule for more complex scenarios
  - Example: Replace `describe port(443) { it { should be_listening } }` with Ansible's `wait_for` module or Molecule verifiers

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for Chef server deployment or consider if Chef server is still needed after migration

### Migration Order

1. **website_https playbook** (already in Ansible, no migration needed)
2. **poodle_fix playbook** (already in Ansible, no migration needed)
3. **InSpec tests** (convert to Ansible-native testing)
4. **Chef deployment scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not to showcase Chef cookbook functionality.
2. The Chef components (InSpec tests and deployment scripts) are the only parts that need migration to Ansible.
3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
4. There is no requirement to maintain backward compatibility with Chef InSpec after migration.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and not used in production.
6. The self-signed certificates are acceptable for the testing environment and don't need to be replaced with CA-signed certificates.
7. The repository doesn't contain any Chef cookbooks or recipes that need migration.