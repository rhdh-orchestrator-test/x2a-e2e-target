# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible playbooks.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that:
  - Set hostname
  - Configure system parameters
  - Install and configure equivalent Ansible automation platform (AWX/Tower)

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables older protocols. Ensure this security hardening is maintained in the migrated solution.
  - Migration approach: Use Ansible's `lineinfile` or `replace` modules to enforce the same configuration.

- **SSH Hardening**: The InSpec test verifies that root login via SSH is disabled.
  - Migration approach: Create an Ansible task that ensures the same configuration and use Ansible's assert module to verify.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar testing capabilities.

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Integrate with third-party compliance tools or develop custom reporting scripts.

- **Self-signed Certificates**: The current implementation generates self-signed certificates using Ansible's openssl modules.
  - Mitigation: Ensure the migrated solution uses the same or equivalent modules to maintain security posture.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - No migration needed, just ensure best practices

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - No migration needed, just ensure best practices

3. **InSpec tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible assertions
   - Implement equivalent compliance reporting

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The primary goal is to move completely away from Chef technologies, including InSpec, to an Ansible-only solution.
2. Compliance reporting is an important aspect that needs to be maintained in the migrated solution.
3. The current implementation is used for demonstration/testing purposes rather than production.
4. The hardcoded credentials in the deployment scripts are not used in production environments.
5. The self-signed certificates are acceptable for the target environment (not production).
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. The migration will maintain or improve the current security posture.