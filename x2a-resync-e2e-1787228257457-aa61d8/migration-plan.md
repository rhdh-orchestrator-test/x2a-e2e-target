# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The repository is primarily educational in nature, containing examples rather than production infrastructure code. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully convert all components to pure Ansible solutions. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates the POODLE SSL vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-compliance**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **ssh-security-compliance**:
    - Description: Chef InSpec test profile that validates SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, CCI compliance validation

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Static HTML content for the website example.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing:
  - Molecule provides similar functionality but is designed specifically for Ansible
  - Will require new configuration files and test execution workflow

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks:
  - Create equivalent Ansible roles for server deployment
  - Use Ansible vault for credential management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should preserve:
  - Self-signed certificate generation
  - TLSv1.2 enforcement
  - Disabling of vulnerable protocols (SSLv3)

- **SSH Hardening**: The InSpec tests validate SSH security. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Maintain compliance with security requirements (CCI-000774)

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic to ensure equivalent coverage.
  - Mitigation: Create a test mapping document to ensure all compliance checks are preserved

- **Test Kitchen to Molecule**: The testing workflow will change, requiring updates to CI/CD pipelines if they exist.
  - Mitigation: Document the new testing process and provide examples

- **Chef Server Deployment**: Replacing the Chef server deployment scripts with Ansible requires understanding of Chef server architecture.
  - Mitigation: Use official Chef documentation to ensure all components are properly configured

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **Testing Framework**: Replace Test Kitchen with Molecule
3. **InSpec Tests**: Convert to Ansible assertions or Molecule verifiers
4. **Deployment Scripts**: Replace with Ansible roles for Chef server deployment

### Assumptions

1. The repository is primarily for educational/demonstration purposes rather than production use
2. There are no external dependencies on these specific InSpec profiles
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. There is no CI/CD pipeline that depends on the current structure
5. The migration goal is to eliminate Chef components entirely, not just to make them work alongside Ansible
6. The self-signed certificates are acceptable for the demonstration environment
7. The hardcoded credentials in deployment scripts are for demonstration only and not used in production