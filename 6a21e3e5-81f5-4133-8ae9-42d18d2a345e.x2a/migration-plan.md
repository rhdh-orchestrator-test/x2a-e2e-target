# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a standardized Ansible approach. The repository primarily consists of:

1. Chef InSpec test profiles for compliance validation
2. Ansible playbooks for web server configuration and security hardening
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** as most of the content is already in Ansible format, with the main work being to convert the Chef InSpec tests to Ansible-compatible testing frameworks and to convert the Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 2-3 weeks for a complete migration, with the following breakdown:
- 1 week: Convert InSpec tests to Ansible-compatible testing (Molecule/TestInfra)
- 1 week: Convert Chef server deployment scripts to Ansible roles
- 3-5 days: Documentation and knowledge transfer

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec profile that validates HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response validation, SSL/TLS protocol validation

- **chef-server-deployment**:
    - Description: Shell script that deploys Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Shell script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, Chef server integration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. This file defines the test environment for validating the Ansible playbooks.

- `index.html`: Simple HTML file used as a test page for the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with TestInfra for infrastructure testing
  - Option 2: Ansible Test modules for validation
  - Option 3: Continue using InSpec but integrate with Ansible using the ansible_inspec module

- **Apache2 (2.4.41-4ubuntu3.10)**: Maintain version-specific package installation in Ansible playbooks

- **OpenSSL**: Maintain current OpenSSL module usage in Ansible playbooks

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 enforcement and SSL3 disablement in the Apache configuration
  - Migration approach: Use the same Ansible module (replace) to modify SSL configuration files

- **SSH Hardening**: The SSH root login restriction must be maintained
  - Migration approach: Convert InSpec test to an Ansible role that both configures and validates SSH settings

- **Self-signed Certificates**: The current approach generates self-signed certificates
  - Migration approach: Maintain the same OpenSSL certificate generation logic in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets (one in each shell script)
  - Type: Username/password pairs for Chef server admin

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with TestInfra which has similar syntax to InSpec, or maintain InSpec as a separate testing tool

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the shell scripts, using Ansible modules for idempotence

- **Test Kitchen Integration**: Ensuring the current Test Kitchen workflow is preserved
  - Mitigation: Continue using Test Kitchen with the Ansible provisioner, or migrate to Molecule for a fully Ansible-native testing approach

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and variable descriptions

2. **poodle_fix playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add documentation and variable descriptions

3. **InSpec tests** (moderate complexity)
   - Convert to Molecule/TestInfra or maintain as InSpec tests with Ansible integration

4. **Chef server deployment scripts** (high complexity)
   - Convert to Ansible roles and playbooks
   - Implement Ansible Vault for credential storage

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "examples" and "companion to a white paper".

2. The InSpec tests are intended to validate the configurations applied by the Ansible playbooks, suggesting a compliance-as-code approach.

3. The Chef server deployment scripts are intended for setting up a Chef environment, which may be redundant after migrating fully to Ansible.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.

5. There is no complex data structure or external data sources being used (no Hiera, no external inventory).

6. The repository does not contain actual Chef cookbooks or recipes, only InSpec tests and Ansible playbooks.

7. The security credentials in the shell scripts are example/placeholder values not intended for production use.