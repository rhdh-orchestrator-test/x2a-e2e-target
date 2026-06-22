# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also contains bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and existing Ansible components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Simple HTML file used for testing web server functionality - can be reused as-is

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Ansible's assert module for basic compliance checks
  - Option 3: Integration with other compliance tools like OVAL or OpenSCAP

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure setup
  - Consider migrating to Ansible Tower/AWX for enterprise automation platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions verified by the InSpec test
  - Convert the InSpec control to Ansible assert or lineinfile checks

- **Certificate Management**: The self-signed certificate generation should be preserved
  - Consider enhancing with Let's Encrypt integration for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions to match InSpec's expectations
  - Consider using Ansible Molecule which provides a more structured testing framework

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Integrate with Ansible Tower/AWX for reporting or implement custom reporting solutions

- **Idempotency**: Ensure all converted scripts maintain idempotency
  - Mitigation: Use Ansible's built-in idempotent modules instead of direct command execution

### Migration Order

1. **website_https.yml** (already in Ansible format, no migration needed)
2. **poodle_fix.yml** (already in Ansible format, no migration needed)
3. **InSpec Tests** (convert to Ansible testing framework)
   - website_https_verify.rb
   - ssh_profile.rb
4. **Chef Deployment Scripts** (convert to Ansible playbooks)
   - deploy-automate.sh
   - deploy-chef-server.sh
5. **Test Kitchen Configuration** (replace with Ansible Molecule or similar)

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production deployment
2. The InSpec tests are intended to validate the Ansible playbook configurations
3. The deployment scripts are meant for setting up test environments
4. No external data sources or complex integrations are present
5. No custom Chef resources or complex Ruby code is used in the InSpec tests
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. The security requirements (like disabling SSLv3) are still relevant and should be maintained
8. No state data needs to be preserved during migration
9. The migration is primarily focused on technology change, not functionality changes