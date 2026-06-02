# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance checks

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-specific testing framework configuration
- `index.html`: Simple HTML file used for testing - can be preserved as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for compliance testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should preserve this security feature.
  - Migration approach: Convert the existing OpenSSL tasks to Ansible modules or roles from Ansible Galaxy

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent tests using Ansible Molecule and testinfra

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework will require careful mapping of test assertions.
  - Mitigation: Use Ansible Molecule with testinfra which provides similar testing capabilities to InSpec

- **Chef Server Deployment**: The Chef server deployment scripts contain Chef-specific commands that need Ansible equivalents.
  - Mitigation: Research Ansible roles for deploying alternative configuration management platforms or create custom roles

### Migration Order

1. **website_https playbook** (low risk, already Ansible) - Verify and optimize existing Ansible playbook
2. **poodle_fix playbook** (low risk, already Ansible) - Verify and optimize existing Ansible playbook
3. **inspec_tests** (moderate complexity) - Convert InSpec tests to Ansible Molecule with testinfra
4. **chef_deployment scripts** (high complexity) - Create Ansible playbooks to replace Chef deployment scripts

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes
2. The InSpec tests are essential and need to be preserved in some form
3. The deployment of Chef Automate/Infra Server is still required, but will be replaced with equivalent Ansible automation
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data migrations are required as this appears to be primarily infrastructure code
8. The security requirements represented in the InSpec tests must be maintained in the migrated solution