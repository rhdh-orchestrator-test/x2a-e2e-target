# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on compliance automation using Chef InSpec alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. No migration needed, can be used as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules for inline validation
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migration.
  - Migration approach: Convert to Ansible roles with the same security parameters

- **SSH Security**: The InSpec tests validate SSH security configurations according to STIG standards.
  - Migration approach: Create equivalent Ansible assertions or testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated during deployment
  - Migration approach: Replace with Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation methods.
  - Mitigation: Use Ansible's assert module or testinfra for functional testing

- **Testing Framework**: Replacing Test Kitchen with Ansible Molecule.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format, just need to be restructured as roles
2. **Testing Framework** - Convert from Test Kitchen to Molecule
3. **InSpec Tests** - Convert to Ansible-native testing methods
4. **Chef Server Deployment Scripts** - Convert bash scripts to Ansible roles

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation.
2. The actual configuration management is already being done with Ansible, so the main migration effort is focused on the testing framework.
3. There are no external dependencies or complex Chef cookbooks to migrate.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The security requirements (TLS 1.2, SSH hardening) need to be maintained in the migrated solution.
6. The Chef server deployment scripts are separate from the main example and may not need to be migrated if the focus is on the compliance automation example.