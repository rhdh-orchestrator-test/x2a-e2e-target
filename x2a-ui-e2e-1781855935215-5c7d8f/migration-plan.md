# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks for web server deployment
2. Converting Chef InSpec tests to Ansible-native testing solutions
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework
  - Molecule provides similar functionality for testing Ansible roles and playbooks

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks
  - Create roles for configuration management platform deployment

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains the only enabled protocol
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: The SSH security controls tested by InSpec need to be implemented in Ansible
  - Create an Ansible task to ensure PermitRootLogin is disabled
  - Implement the same security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Challenge: Maintaining the same level of validation detail
  - Mitigation: Use Ansible's uri module for HTTP checks and command module with OpenSSL for SSL validation

- **Compliance Reporting**: InSpec provides compliance reporting that needs an equivalent in Ansible
  - Challenge: Finding a suitable replacement for compliance reporting
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or OpenSCAP

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and optimize existing playbooks
   - Convert to roles for better organization

2. **Testing Framework** (kitchen.yml) - Medium complexity
   - Replace Test Kitchen with Molecule
   - Set up equivalent test scenarios

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assertions or Molecule verifiers
   - Ensure all security checks are preserved

4. **Chef Automate/Server Deployment** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible roles for deployment of a configuration management platform
   - Implement secure credential management

### Assumptions

1. The current setup uses Chef InSpec only for testing, not for actual configuration management
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There is no integration with external systems beyond what's visible in the code
4. The self-signed certificates are acceptable for the target environment
5. No specific performance requirements are needed for the Apache web server
6. The Chef Automate/Server deployment is for a development or test environment, given the hardcoded credentials
7. The migration does not need to preserve the Chef Automate/Server functionality, but rather replace it with an Ansible-based solution