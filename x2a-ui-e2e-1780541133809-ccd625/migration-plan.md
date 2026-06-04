# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used for testing the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for simple assertions
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Integrate with other testing frameworks like Testinfra or ServerSpec

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platforms

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the only enabled protocol
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by the InSpec profile need to be implemented in Ansible
  - Ensure PermitRootLogin is properly configured
  - Maintain compliance with STIG requirements (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing will require careful mapping of assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Validation**: Ensuring that the migrated solution maintains the same level of compliance validation
  - Mitigation: Create a compliance matrix to track requirements before and after migration

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **InSpec Tests** (convert to Ansible-native testing)
   - website_https_verify.rb
   - ssh_profile.rb
4. **Chef Deployment Scripts** (convert to Ansible playbooks)
   - deploy-automate.sh
   - deploy-chef-server.sh
5. **Test Kitchen Configuration** (replace with Molecule)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The deployment scripts are examples and contain placeholder credentials that would be replaced in a production environment.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. There are no external dependencies or integrations beyond what is explicitly shown in the repository.
5. The migration will maintain the same level of functionality and security validation.
6. The hardcoded values in the deployment scripts (hostname, username, password) are placeholders and will be properly secured in the migrated solution.
7. The repository does not contain any custom Chef resources or complex Chef-specific functionality that would require special handling during migration.