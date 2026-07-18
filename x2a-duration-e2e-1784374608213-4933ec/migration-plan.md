# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The main complexity comes from replacing Chef InSpec testing with equivalent Ansible testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL/TLS configuration and InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache deployment, SSL configuration, security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

**CRITICAL PATH VERIFICATION:**
All module paths listed above have been verified to exist in the repository using the `list_directory` tool.

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS configuration. Need to be converted to Ansible-native testing (Molecule, pytest).
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Need to be converted to Ansible-native testing.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-lint for static code analysis
  - Option 3: pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible collections for configuration management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the same level of security for Apache SSL configuration, particularly the TLS protocol restrictions (disabling SSLv3, enabling TLSv1.2).
  - Migration approach: Preserve the same configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec profile for SSH security must be converted to equivalent Ansible checks.
  - Migration approach: Use ansible-lint rules or custom Ansible roles for SSH hardening

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, possibly with ansible-vault or an external secrets manager
  - Count of credentials detected: 3 (username, password, SSL certificates)

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation: Create equivalent tests using Ansible Molecule and its verifier plugins

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced with Ansible equivalents.
  - Mitigation: Map Chef Automate features to Ansible AWX/Tower features and identify any gaps

- **Compliance Reporting**: Chef InSpec provides compliance reporting that needs an equivalent in the Ansible ecosystem.
  - Mitigation: Investigate Ansible AWX/Tower compliance capabilities or integrate with tools like OpenSCAP

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to the new Ansible structure
   - Update any deprecated Ansible syntax

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible Molecule tests
   - Ensure test coverage is maintained

3. **Chef Deployment Scripts** (Higher complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Replace Chef-specific functionality with Ansible equivalents

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
4. The Chef Automate/Infra Server functionality is being replaced with Ansible AWX/Tower
5. No custom Chef cookbooks or resources are being used beyond what's visible in the repository
6. The InSpec tests are comprehensive and should be fully converted to maintain the same level of testing
7. The hardcoded credentials in the scripts are for demonstration purposes and will be properly secured in the migrated solution