# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with Chef InSpec tests and Chef server deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for integration testing
  - Use Ansible's `assert` module for validation checks
  - Consider Molecule for test-driven development
  - Alternatively, use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in inventory management for multi-node testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Ansible Tower for web UI and control
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement
  - Ensure proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
  - Convert InSpec tests to Ansible assertions or molecule tests
  - Ensure PermitRootLogin setting is properly enforced

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - 2 credential sets identified (username/password for Chef user creation)

### Technical Challenges

- **Test Conversion**: Converting InSpec tests to Ansible-native testing requires careful mapping of assertions
  - Challenge: InSpec has specific matchers for SSL/TLS testing
  - Mitigation: Use Ansible's uri module with appropriate SSL parameters and custom assertions

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality
  - Challenge: Chef Server provides specific organizational structure and authentication mechanisms
  - Mitigation: Document clear mapping between Chef Server concepts and Ansible equivalents (AWX/Tower)

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update as needed for best practices
   - Update any deprecated modules or syntax

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all security checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity
   - Convert to Ansible roles for infrastructure deployment
   - Replace Chef-specific functionality with Ansible equivalents
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The security requirements enforced by the InSpec tests are still valid and must be maintained
3. A replacement for Chef Automate's visualization and reporting capabilities will be needed
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates approach is acceptable for the migrated solution
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with proper secret management
7. The migration will not change the fundamental architecture of the deployed applications