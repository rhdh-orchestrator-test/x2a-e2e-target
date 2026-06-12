# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Sample HTML file used for testing the web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate to Ansible Molecule for testing infrastructure
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for functional testing
  - Alternatively, maintain InSpec tests but run them from Ansible using the `inspec` command

- **Test Kitchen with Vagrant**: Replace with Ansible-native testing solutions:
  - Migrate to Ansible Molecule for test orchestration
  - Continue using Vagrant as a driver or switch to Docker for faster testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain compliance with security standards referenced in InSpec tests

- **SSH Security**: Maintain SSH hardening requirements from the InSpec tests
  - Ensure root login remains disabled
  - Preserve STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-native testing will require careful mapping of assertions
  - Challenge: InSpec has specific matchers for SSL/TLS protocols that may not have direct equivalents in Ansible testing frameworks
  - Mitigation: May need to write custom Ansible modules or use shell commands with appropriate parsing

- **Compliance Reporting**: InSpec provides rich compliance reporting capabilities
  - Challenge: Maintaining the same level of compliance reporting in Ansible
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or maintaining InSpec for compliance testing while using Ansible for remediation

### Migration Order

1. **website_https.yml** (Priority 1, already in Ansible format)
   - Minimal changes needed, just refactoring for best practices

2. **poodle_fix.yml** (Priority 1, already in Ansible format)
   - Minimal changes needed, just refactoring for best practices

3. **Chef Automate Deployment Scripts** (Priority 2)
   - Convert bash scripts to Ansible roles for Chef server deployment
   - Consider if Chef Automate/Server is still needed or if this can be replaced with Ansible automation

4. **InSpec Tests** (Priority 3)
   - Migrate to Ansible testing frameworks or maintain as separate InSpec tests

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies where possible
2. The InSpec tests are used for compliance validation and may need to be maintained or replaced with equivalent functionality
3. The deployment scripts for Chef Automate and Chef Server may be deprecated if the organization is fully migrating to Ansible
4. The target environment will remain Ubuntu 20.04 or similar Linux distributions
5. The security requirements and compliance standards referenced in the InSpec tests must be maintained in the Ansible implementation
6. Test Kitchen and Vagrant are used for development and testing but may not be part of the production deployment process