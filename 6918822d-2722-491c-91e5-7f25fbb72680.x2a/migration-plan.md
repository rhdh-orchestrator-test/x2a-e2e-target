# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for configuring web servers with HTTPS. The repository also includes Chef Automate and Chef Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks given the limited scope and straightforward configurations.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-https-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG references

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Ansible's community.general.test_module for more complex testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening that disables vulnerable SSL protocols
- **SSH Hardening**: The SSH security checks need to be implemented in Ansible
- **Self-signed Certificates**: The certificate generation process should be maintained in the Ansible migration
- **User Management**: The Chef user and organization creation needs to be translated to Ansible user management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities may require additional modules or custom scripts
- **Chef Automate Replacement**: Determining an appropriate replacement for Chef Automate's compliance reporting functionality within the Ansible ecosystem

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible testing framework
3. Chef Server/Automate Setup Scripts - Replace with Ansible roles for configuration management platform setup

### Assumptions

1. The primary purpose of this repository is demonstrating compliance automation with Chef InSpec alongside Ansible
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The self-signed certificates are for testing purposes only and not production use
5. The hardcoded credentials in the setup scripts are for demonstration purposes only
6. No state data or databases need to be migrated
7. The migration will maintain the same level of security compliance checking
8. Test Kitchen is only used for development/testing and not in production pipelines