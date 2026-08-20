# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Compliance testing for SSH configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL/TLS protocol security

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `README.md`: Repository overview
- `chef-and-ansible/README.md`: Description of the Chef InSpec and Ansible integration examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use ansible-lint for static code analysis
  - Option 3: Integrate with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be maintained in the migrated Ansible playbooks.
  - Migration approach: Preserve the same SSL/TLS configuration in the Ansible tasks

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible task to enforce this configuration and add verification

- **Self-signed Certificates**: The playbook generates self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) for certificate management

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible assert modules or Molecule verify phase to implement equivalent tests

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (convert to Ansible testing framework, moderate complexity)
4. **Chef Deployment Scripts** (convert to Ansible playbooks, higher complexity)

### Assumptions

1. The repository is primarily for demonstration purposes showing Chef InSpec with Ansible integration
2. The actual infrastructure being managed is relatively simple (web servers with HTTPS)
3. There's no complex Chef cookbook structure that needs migration
4. The Chef Automate and Chef Infra Server deployment scripts may be optional to migrate if the target environment will not use Chef for configuration management
5. The Test Kitchen setup is used for development and testing only
6. No external data sources or complex variable structures are being used
7. No complex inventory management is present in the current setup