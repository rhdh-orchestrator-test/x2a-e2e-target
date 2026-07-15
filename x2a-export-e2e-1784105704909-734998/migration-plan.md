# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, as referenced in the README. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-native testing solutions
2. Consolidating the Chef Automate/Chef Server deployment scripts into Ansible playbooks
3. Preserving the existing Ansible playbooks while enhancing them with testing capabilities

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

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
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

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
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic validation
  - Option 2: Implement Molecule for comprehensive testing
  - Option 3: Use the community.general.test_connection module for service availability testing

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Playbook integration tests with custom verification tasks

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks:
  - Create roles for system preparation (sysctl settings)
  - Create playbooks for deploying alternative compliance platforms (options below)

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH security profile must be maintained
  - Migrate the InSpec SSH checks to Ansible assert tasks
  - Consider expanding SSH hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the detailed InSpec tests to equivalent Ansible validation
  - Mitigation: Use a combination of uri, command, and assert modules to replicate InSpec functionality
  - Consider implementing custom Ansible modules if needed for complex validations

- **Compliance Reporting**: Chef InSpec provides compliance reporting capabilities
  - Mitigation: Implement alternative compliance reporting using Ansible facts and custom reporting templates
  - Consider integration with tools like AWX/Tower for compliance dashboards

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as they remain largely unchanged
   - Add inline testing capabilities to replace separate InSpec tests

2. **InSpec Test Profiles** (website_https_verify.rb, ssh_profile.rb)
   - Convert to Ansible assert tasks or Molecule tests
   - Integrate with existing playbooks

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh)
   - Highest complexity due to complete technology change
   - Create Ansible roles for system configuration and alternative compliance tooling

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. The security requirements (TLS configuration, SSH hardening) must be maintained in the migrated solution
5. No external Chef cookbooks or complex Chef-specific features are in use beyond what's visible in the repository
6. The team is willing to adopt alternative compliance testing approaches within Ansible
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migration