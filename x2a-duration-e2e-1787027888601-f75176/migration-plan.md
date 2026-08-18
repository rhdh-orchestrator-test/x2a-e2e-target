# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Chef InSpec for compliance testing and Ansible playbooks for configuration management. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating compliance and security

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Simple HTML template for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use pytest-ansible for Python-based testing
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Maintain kitchen.yml but use the ansible_playbook provisioner only

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks:
  - Create Ansible roles for configuration management
  - Use Ansible collections for compliance automation

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Convert the SSH InSpec profile to Ansible security checks
  - Implement equivalent checks for PermitRootLogin settings
  - Preserve compliance with security standards (STIG)

- **Vault/secrets management**:
  - Current implementation uses hardcoded credentials in deployment scripts
  - Migrate to Ansible Vault for secure credential storage
  - Identified credentials:
    - User password in deploy-automate.sh and deploy-chef-server.sh (2 instances)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Challenge: InSpec has specific matchers and resources that may not have direct equivalents
  - Mitigation: Use Ansible assert modules with custom conditions or develop custom modules

- **Compliance Reporting**: Replacing Chef InSpec compliance reporting capabilities
  - Challenge: InSpec provides structured compliance reporting that Ansible doesn't natively support
  - Mitigation: Integrate with tools like Ansible AWX/Tower for compliance reporting or use community collections

- **Self-Signed Certificates**: Maintaining proper certificate generation
  - Challenge: Ensuring the openssl_* modules are used correctly in Ansible
  - Mitigation: Verify certificate generation works correctly in the target environment

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as they are already in Ansible format
   - May need minor updates for newer Ansible versions

2. **Testing Framework**
   - Convert InSpec tests to Ansible-compatible testing
   - Implement equivalent assertions and checks

3. **Deployment Scripts**
   - Convert Chef Automate/Server deployment scripts to Ansible playbooks
   - Implement secure credential management

### Assumptions

1. The target environment will continue to use Ubuntu 20.04 or compatible Linux distributions
2. The migration will maintain the same level of security compliance checking
3. Self-signed certificates are acceptable for the web server configuration
4. The Chef Automate/Server deployment is part of the migration scope
5. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
6. The existing Ansible playbooks are compatible with current Ansible versions
7. Test Kitchen is only used for development/testing and not in production