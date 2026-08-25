# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the infrastructure code is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on testing and validation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security compliance
- `index.html`: Sample HTML file for testing web server configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra
  - For compliance testing: Use ansible-lint with custom rules or OpenSCAP with Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for orchestration
  - AWX/Tower for web UI and API
  - Git repositories for playbook storage

### Security Considerations

- **SSL Configuration**: The existing playbooks already implement TLS 1.2 and disable insecure protocols. This security practice should be maintained in the migrated Ansible playbooks.
  
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This check should be implemented as an Ansible task that both configures and verifies this setting.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely using Ansible Vault or an external certificate management system
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions to ensure equivalent coverage.
  - Mitigation: Create a test mapping document and validate each test case individually.

- **Chef Server Deployment**: Replacing the Chef server deployment scripts with Ansible playbooks will require understanding the specific requirements and configurations.
  - Mitigation: Create an Ansible role that installs and configures the necessary components, with variables for customization.

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Update any deprecated syntax or modules

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Update any deprecated syntax or modules

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible Molecule/Testinfra
   - Convert ssh_profile.rb to Ansible security role with verification

4. **Chef server deployment scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration and educational purposes rather than production deployment, based on the README content.
2. The Chef InSpec tests are used for compliance verification of systems managed by Ansible, not Chef-managed systems.
3. The deployment scripts are used for setting up Chef infrastructure, not for deploying applications.
4. No external dependencies or modules are required beyond what's included in the repository.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing.
6. No complex data structures or external data sources are used for configuration.
7. The migration will maintain the same level of security and compliance checking as the original implementation.