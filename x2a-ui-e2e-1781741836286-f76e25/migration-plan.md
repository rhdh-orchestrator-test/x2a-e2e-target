# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

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
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be kept as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using the community.general.test_connection module for connectivity tests

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning can be handled by OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older, vulnerable protocols

- **SSH Security**: The SSH root login compliance check must be preserved:
  - Convert the InSpec control to an Ansible task that checks the same configuration
  - Implement remediation in the same playbook

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-native solutions while maintaining the same level of compliance validation:
  - InSpec provides rich testing capabilities specifically designed for compliance
  - Ansible's testing capabilities are more focused on state validation
  - Solution: Consider using a combination of Ansible assert module and custom scripts, or maintain InSpec as a separate tool called from Ansible

- **Certificate Management**: Ensuring proper handling of SSL certificates:
  - The current solution generates self-signed certificates
  - Migration should maintain this capability while improving security practices
  - Solution: Use Ansible's crypto modules (openssl_*) which are already in use

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **Chef InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible playbooks)

### Assumptions

1. The primary goal is to consolidate on Ansible and eliminate Chef dependencies
2. Compliance testing is a critical requirement that must be maintained
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible automation for a different configuration management solution
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. Self-signed certificates are acceptable for the HTTPS configuration
6. The security standards referenced in the SSH profile (SRG-OS-000112, etc.) must continue to be enforced
7. No external data sources or databases are involved in the current setup
8. The migration will not change the fundamental architecture of the applications being deployed