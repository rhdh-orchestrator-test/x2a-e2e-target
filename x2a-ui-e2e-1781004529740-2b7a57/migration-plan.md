# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in place) and medium complexity for converting the InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing the web server. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-compliance if advanced compliance features are needed

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Apache2 (2.4.41-4ubuntu3.10)**: Keep using Ansible's apt module with specific version

- **OpenSSL**: Keep using Ansible's openssl_* modules

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables vulnerable protocols (SSLv3) and enables only TLSv1.2
  - Migration approach: Use Ansible's template module with proper validation

- **SSH Security**: The compliance checks for SSH root login must be maintained
  - Migration approach: Convert InSpec tests to Ansible assert tasks or include in ansible-lint checks

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Migration approach: Continue using Ansible's openssl_* modules or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex scenarios

- **Compliance Reporting**: InSpec provides rich compliance reporting that may be lost in migration
  - Mitigation: Consider implementing ansible-compliance or integrating with a compliance tool that works with Ansible

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible equivalents
  - Mitigation: Create Ansible roles that perform equivalent setup tasks for configuration management

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Add documentation and comments

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assert tasks or Molecule tests
   - Convert ssh_profile.rb to Ansible security checks

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible for compliance automation, not for production deployment.

2. The InSpec tests are used for compliance verification rather than functional testing.

3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. The Apache configuration and SSL setup are simplified examples and may need enhancement for production use.

6. The migration will focus on maintaining the same functionality while moving to Ansible-native solutions where possible.

7. There is no complex state management or data persistence requirements beyond the basic web server configuration.

8. The Chef Automate and Chef Server deployment may not be needed if moving entirely to Ansible for both configuration management and compliance.