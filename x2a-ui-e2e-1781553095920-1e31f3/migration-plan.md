# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-native testing solutions
2. Preserving the existing Ansible playbooks with minimal changes
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that most of the infrastructure code is already in Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate to [ansible-lint](https://github.com/ansible/ansible-lint) for static analysis
  - Use [Molecule](https://molecule.readthedocs.io/) with [Testinfra](https://testinfra.readthedocs.io/) for functional testing
  - Consider [ansible-test](https://docs.ansible.com/ansible/latest/dev_guide/testing_integration.html) for integration testing

- **Test Kitchen**: Replace with Molecule for test orchestration
  - Molecule can use Vagrant as a driver similar to Test Kitchen

- **Chef Automate/Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Ansible Collections for role management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the Apache configuration
  - Consider expanding to include additional modern security best practices

- **SSH Hardening**: The SSH security controls tested by the InSpec profile need to be implemented in Ansible
  - Create an equivalent Ansible role for SSH hardening
  - Implement Ansible tests to validate the SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Testinfra Migration**: Converting Ruby-based InSpec tests to Python-based Testinfra
  - Challenge: Maintaining the same level of readability and expressiveness
  - Mitigation: Create a mapping of InSpec resources to Testinfra modules and carefully test each conversion

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting capabilities
  - Challenge: Replicating compliance reporting functionality in Ansible
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with compliance tools like OpenSCAP

- **Test Kitchen to Molecule**: Converting the test orchestration workflow
  - Challenge: Ensuring the same level of test isolation and repeatability
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **Test Infrastructure**: Implement Molecule and Testinfra framework to replace Test Kitchen
3. **InSpec Tests**: Convert InSpec tests to Testinfra tests
4. **Chef Automate/Server Scripts**: Replace with Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The migration will maintain or improve the current security posture
5. The self-signed certificates are for testing only and would be replaced with proper certificates in production
6. The hardcoded credentials in the setup scripts are for demonstration purposes only
7. The SSH hardening profile is a sample and may need to be expanded for production use
8. The repository is primarily for demonstration/educational purposes rather than production deployment