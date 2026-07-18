# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low to medium complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible-module**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers
    - Path: chef-and-ansible
    - Technology: Chef InSpec (tests) and Ansible (playbooks)
    - Key Features: HTTPS configuration testing, SSL/TLS protocol validation, SSH security compliance checks

- **setup-automate-module**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef server installation, user creation, organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS on Apache. Migration consideration: Keep as-is, but update to use Ansible collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Keep as-is, but update to use Ansible collections.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Convert to Ansible Molecule verify tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule verify tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible Assert module for inline testing
  - Option 3: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Ansible collections for configuration management

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration approach: Maintain this security hardening in Ansible playbooks.
  
- **SSH Security**: InSpec tests verify SSH root login is disabled. Migration approach: Convert to Ansible assert or Molecule verify tests.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Migration approach: Maintain this functionality using Ansible's openssl modules.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password). Migration approach: Replace with Ansible Vault for secure credential storage.
  - SSL certificates and keys. Migration approach: Use Ansible Vault or external secret management.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require different approaches for different test types:
  - Simple assertions can use Ansible's assert module
  - Complex compliance tests may require custom modules or external tools
  - Mitigation: Consider a phased approach, starting with simple tests

- **Chef Server Deployment**: The Chef server deployment scripts contain specific Chef commands that need Ansible equivalents:
  - Mitigation: Create Ansible roles for AWX/Tower deployment with similar functionality

### Migration Order

1. **Ansible Playbooks** (Low risk): Update existing Ansible playbooks to use current Ansible collections and best practices
2. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible-compatible testing framework
3. **Chef Server Deployment Scripts** (High complexity): Convert to Ansible playbooks for deploying alternative infrastructure

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, eliminating Chef dependencies.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and only need minor updates.
3. Test Kitchen is only used for development/testing and not in production pipelines.
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up infrastructure that will be replaced by Ansible AWX/Tower or another orchestration solution.
5. The security compliance requirements currently tested by InSpec will need to be maintained in the Ansible solution.
6. The target environment (Ubuntu 20.04) will remain the same after migration.