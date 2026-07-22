# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with both Chef and Ansible components. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository includes Ansible playbooks for configuring web servers with HTTPS, Chef InSpec tests for verification, and shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve standardizing on pure Ansible practices and migrating the Chef InSpec tests to Ansible-native testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL protocol testing

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `README.md`: Documentation files that explain the purpose of the repository. Will need updating to reflect the new Ansible-only approach.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider OpenSCAP with Ansible or ansible-lint with custom rules
  - For continuous testing: Integrate with CI/CD using ansible-test

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for:
  - Configuration management tracking
  - Compliance reporting
  - Consider migrating to AWX/Ansible Tower for similar functionality

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configurations that must be preserved:
  - Self-signed certificate generation
  - Protocol security (disabling vulnerable protocols like SSLv3)
  - These should be migrated to Ansible roles with proper variable management

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Root login restrictions
  - Compliance with security standards (SRG-OS-000112, V-38607)
  - Migrate to Ansible roles that both configure and verify these settings

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Replace with Ansible Vault for secure credential storage
  - Total credentials detected: 2 (username/password pairs in deployment scripts)

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-native testing frameworks:
  - Challenge: InSpec has specific syntax for compliance testing
  - Mitigation: Use Ansible assert modules or integrate with tools like Testinfra

- **Maintaining Compliance Standards**: Ensuring the same level of compliance verification:
  - Challenge: InSpec directly maps to compliance standards (CCI-000774, etc.)
  - Mitigation: Document compliance mappings in Ansible roles and use tags/metadata

- **Deployment Script Conversion**: Converting bash deployment scripts to idempotent Ansible roles:
  - Challenge: Ensuring proper error handling and idempotence
  - Mitigation: Use Ansible modules like command with changed_when conditions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; focus on refactoring to follow best practices
2. **Test Framework**: Set up Molecule testing framework to replace Test Kitchen
3. **InSpec Tests**: Convert InSpec tests to Ansible-native testing
4. **Deployment Scripts**: Convert Chef server deployment scripts to Ansible roles

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The InSpec tests are used for verification rather than continuous compliance monitoring
3. There are no external dependencies or integrations not visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. No actual Chef cookbooks or recipes are in use beyond the deployment scripts
6. The deployment scripts are used for setting up test environments rather than production systems