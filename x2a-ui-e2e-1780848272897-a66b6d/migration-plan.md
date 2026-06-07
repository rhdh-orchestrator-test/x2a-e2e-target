# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on compliance automation using Chef InSpec alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The primary migration effort will involve replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and existing Ansible content.

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
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for more complex test scenarios
  - For compliance testing, consider using OpenSCAP with Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Preserve the same Apache configuration in the Ansible playbooks

- **SSH Security Controls**: The SSH root login restriction must be maintained
  - Approach: Convert the InSpec control to an Ansible task that ensures the same configuration

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Approach: Maintain the same approach or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible assert modules and Molecule for testing, or consider maintaining InSpec as a testing tool even after migrating configuration management to Ansible

- **Chef Automate/Server Deployment**: Replacing Chef Automate and Chef Server deployment scripts
  - Mitigation: Create Ansible roles for deploying alternative compliance and configuration management tools, or maintain these scripts if Chef Automate/Server will still be used for compliance reporting

### Migration Order

1. **website_https.yml** (already in Ansible format, no migration needed)
2. **poodle_fix.yml** (already in Ansible format, no migration needed)
3. **website_https_verify.rb** (convert InSpec tests to Ansible Molecule tests)
4. **ssh_profile.rb** (convert InSpec control to Ansible task and test)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible roles if Chef Automate/Server is being replaced)

### Assumptions

1. The primary goal is to migrate away from Chef InSpec while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
3. The deployment scripts for Chef Automate and Chef Server may or may not need migration, depending on whether these tools will continue to be used
4. The target environment will remain Ubuntu 20.04 running on Vagrant VMs
5. The security requirements (TLS 1.2, disabled root SSH login) must be maintained in the migrated solution
6. No external dependencies or complex configurations exist beyond what is visible in the repository
7. The migration will need to address the hardcoded credentials in the deployment scripts