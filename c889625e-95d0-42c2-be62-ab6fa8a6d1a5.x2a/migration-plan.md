# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate and Chef Infra Server deployment scripts to Ansible

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The repository appears to be primarily educational/demonstration in nature rather than a production infrastructure codebase.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL vulnerabilities (POODLE) in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test website
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider migrating to ansible-test for comprehensive testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Use Molecule's Vagrant driver to maintain similar VM provisioning workflow

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline orchestration

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper file permissions for certificates (mode 0640)
  - TLS 1.2 enforcement and disabling of insecure protocols

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled in Ansible-managed configurations
  - Maintain compliance with security requirements referenced in the InSpec test (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef server deployment scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic
  - Mitigation: Use Ansible's assert module with carefully crafted conditions to match InSpec expectations

- **Certificate Management**: The current solution uses OpenSSL modules for certificate generation
  - Mitigation: Ansible has built-in OpenSSL modules that can be used directly with minimal changes

- **Compliance Reporting**: Loss of Chef InSpec's structured compliance reporting
  - Mitigation: Consider integrating with compliance tools like OpenSCAP or using Ansible Automation Platform's compliance features

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes
2. **Chef Server Deployment Scripts**: Convert bash scripts to Ansible roles for infrastructure provisioning
3. **InSpec Tests**: Convert to Ansible-compatible testing framework last, as they validate the other components

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production use
2. The existing Ansible playbooks are functional and follow best practices
3. There are no additional Chef cookbooks or recipes beyond what's visible in the repository
4. The InSpec tests are used for validation only and not integrated into a larger compliance framework
5. The deployment scripts are used for setting up test environments rather than production systems
6. No external dependencies or third-party modules are required beyond what's explicitly referenced
7. The hardcoded credentials in deployment scripts are for demonstration purposes only