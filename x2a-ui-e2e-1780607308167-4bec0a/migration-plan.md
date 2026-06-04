# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Chef InSpec tests and Ansible playbooks. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating Chef Automate/Chef Server deployment scripts into Ansible playbooks
3. Preserving the existing Ansible playbooks while enhancing them with integrated testing

Given the limited scope and the fact that most of the infrastructure code is already in Ansible format, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks** for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require replacing with Ansible-native testing frameworks.
- `index.html`: Simple HTML file used as a test page. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Integrate with other testing frameworks like ServerSpec or BATS

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles that can:
  - Install and configure equivalent monitoring and compliance solutions
  - Consider alternatives like AWX/Ansible Tower for web UI and control

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **SSH Hardening**: Preserve the SSH security controls from ssh_profile.rb
  - Migrate the InSpec control to an Ansible task that ensures PermitRootLogin is not set to 'yes'
  - Consider expanding SSH hardening with an Ansible role like dev-sec.ssh-hardening

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: Preserving the same level of testing coverage and readability
  - Mitigation: Use Molecule with testinfra which has similar syntax to InSpec

- **Compliance Reporting**: InSpec provides rich compliance reporting capabilities
  - Challenge: Finding equivalent compliance reporting in Ansible ecosystem
  - Mitigation: Consider integrating with compliance tools like OpenSCAP or using AWX/Tower for reporting

- **Certificate Management**: The current solution generates self-signed certificates
  - Challenge: Maintaining secure certificate management practices
  - Mitigation: Consider integrating with Ansible roles for Let's Encrypt or other certificate management solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to convert to Ansible roles

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
3. Vagrant will continue to be used for development/testing environments
4. Self-signed certificates are acceptable for the testing environment
5. The hardcoded credentials in deployment scripts are for demonstration purposes only
6. There are no external dependencies or integrations not visible in the repository
7. The migration does not need to preserve Chef Automate/Server functionality but rather replace it with Ansible equivalents