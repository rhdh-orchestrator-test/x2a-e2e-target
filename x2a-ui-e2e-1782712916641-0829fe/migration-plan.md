# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests that verify HTTPS functionality and security of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **inspec-ssh-profile**:
    - Description: Chef InSpec compliance profile that checks SSH configuration for security compliance (specifically root login settings)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that:
  - Configure system settings (hostname, sysctl parameters)
  - Install alternative compliance and infrastructure management tools

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older, vulnerable protocols

- **SSH Hardening**: The SSH compliance checks in ssh_profile.rb must be maintained:
  - Convert the InSpec control for SSH root login to equivalent Ansible assertions
  - Preserve the STIG compliance references for documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username: jtonello, password: password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely, possibly using ansible-vault

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires careful mapping of test assertions:
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Create reusable Ansible test modules or roles that provide similar functionality

- **Compliance Reporting**: InSpec provides rich compliance reporting capabilities:
  - Challenge: Maintaining compliance reporting capabilities in Ansible
  - Mitigation: Integrate with tools like Ansible AWX/Tower for reporting or use community modules for compliance reporting

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality:
  - Challenge: Chef Server provides a centralized configuration management database
  - Mitigation: Consider using Ansible AWX/Tower or other Ansible-compatible configuration management databases

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible playbooks for infrastructure setup

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies, not to change the functionality of the existing configurations.
2. The InSpec tests are used primarily for validation and could be replaced with equivalent Ansible testing mechanisms.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The self-signed certificates approach is acceptable for the migrated solution.
5. The hardcoded credentials in the Chef deployment scripts are for demonstration purposes and will be replaced with proper secret management in the Ansible implementation.
6. The STIG compliance requirements referenced in the SSH profile are still applicable and need to be maintained in the Ansible implementation.