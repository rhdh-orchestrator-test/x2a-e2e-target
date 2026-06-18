# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The primary migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_compliance_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS content verification, SSL protocol verification, SSH root login verification

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Simple HTML file used for testing web server - can be reused as-is

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles
  - Option 2: Ansible's assert module for basic compliance checks
  - Option 3: Integration with other compliance tools like OVAL or OpenSCAP

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Compliance as Code

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Migration approach: Preserve the same Apache SSL configuration in Ansible tasks

- **SSH Hardening**: The InSpec test verifies that SSH root login is disabled
  - Migration approach: Create equivalent Ansible tasks to verify and enforce this setting

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules (already in use) to maintain the same functionality

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count of credentials detected: 3 (username, password, organization name in deploy scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Verification**: Ensuring that all compliance checks are properly translated
  - Mitigation: Create a compliance matrix to track each control and its implementation in the new system

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality
  - Mitigation: Identify which Chef Server features are actually being used and implement only those needed

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec tests** (moderate complexity, requires translation to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires architectural decisions about replacement)

### Assumptions

1. The primary purpose of this repository is demonstration/example code rather than production infrastructure
2. The InSpec tests are used for compliance verification of configurations managed by Ansible
3. The Chef Automate/Infra Server deployment is separate from the main Ansible+InSpec workflow
4. There are no external dependencies or integrations not visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The security requirements (TLS 1.2, SSH hardening) must be maintained in the migrated solution
7. No state data or databases need to be migrated as part of this process