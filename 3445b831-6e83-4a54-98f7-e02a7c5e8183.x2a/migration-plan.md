# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity since most of the content is already in Ansible format.

## Module Migration Plan

This repository contains a combination of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI)

- **automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier
- `index.html`: Simple HTML file that appears to be part of the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule for testing
  - **Option 2**: Use ansible-test framework
  - **Option 3**: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - **Option 1**: Migrate to Ansible Molecule for infrastructure testing
  - **Option 2**: Use ansible-test with docker or vagrant drivers

- **Chef Automate/Infra Server**: Replace with Ansible automation solutions:
  - **Option 1**: Migrate to Ansible Automation Platform (AAP)
  - **Option 2**: Use AWX (open-source version of Ansible Tower)
  - **Option 3**: Use GitLab CI/CD or Jenkins with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Ansible Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module or Molecule to create equivalent tests
  - Consider using the ansible.builtin.uri module to replace the HTTP tests
  - For SSL tests, use Ansible's openssl_certificate_info module

- **Challenge 2**: Replacing Chef Automate/Infra Server deployment
  - Mitigation: Create Ansible playbooks to deploy alternative infrastructure management solutions
  - Consider using AWX/Ansible Tower as a replacement for Chef Automate

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-native testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Create equivalent Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The deployment scripts are examples and not used in production (they contain hardcoded credentials).
4. The migration will maintain the same functionality but using Ansible-native solutions.
5. The existing Ansible playbooks can be reused with minimal modifications.
6. The InSpec tests need to be converted to Ansible-native testing solutions.
7. The deployment scripts need to be replaced with Ansible playbooks that deploy alternative solutions.