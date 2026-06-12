# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests used for compliance validation
2. Chef Automate/Chef Server deployment scripts

The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and medium complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_website_tests**:
    - Description: Chef InSpec tests that validate HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL protocol security validation

- **inspec_ssh_profile**:
    - Description: Chef InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef_automate_deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use simple Vagrant or Docker-based testing with Ansible playbooks directly

- **Chef Automate/Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to Ansible Tower/AWX
  - Option 2: Use Ansible Automation Platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Ensure the same SSL protocol restrictions are applied in the migrated Ansible roles

- **SSH Security**: The SSH compliance checks must be maintained
  - Approach: Convert InSpec SSH tests to Ansible-compatible tests or use ansible-lint security checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Ansible assert modules or integrate with pytest-ansible for similar functionality
  - Consider maintaining InSpec as a separate testing tool if complex compliance requirements exist

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Implement Ansible Automation Platform with compliance scanning or integrate with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Action: Review and optimize existing playbooks, convert to roles if appropriate
   - Timeline: 1-2 days

2. **Testing Framework** (InSpec tests): Medium complexity
   - Action: Convert InSpec tests to Ansible-compatible testing framework
   - Timeline: 3-5 days

3. **Chef Automate/Server Deployment**: High complexity
   - Action: Create Ansible playbooks to deploy Ansible Automation Platform or alternative solution
   - Timeline: 5-7 days

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The Chef components (InSpec, Automate, Server) are being used primarily for compliance testing and reporting
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. No complex Chef cookbooks or recipes are present that would require significant logic translation
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The self-signed certificates are for testing environments, not production
7. The migration will maintain the same level of security validation currently provided by InSpec tests
8. The SSH compliance profile is based on STIG standards which should be maintained in the Ansible implementation