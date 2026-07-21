# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks with Chef InSpec testing that need to be migrated to a pure Ansible solution. The migration scope is relatively small, consisting of two Ansible playbooks for configuring Apache web servers with HTTPS and fixing SSL vulnerabilities, along with InSpec tests for verification. The repository also includes Chef Automate and Chef Infra Server setup scripts that will need to be converted to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and their straightforward functionality.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

**CRITICAL PATH VERIFICATION:**
No Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), or PowerShell modules (.psd1) were found in the repository. The file searches returned no results for these patterns:
- **/manifests/init.pp
- **/recipes/default.rb
- **/*.psd1

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible Molecule for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS configuration. Will need to be converted to Ansible assertions or Molecule verifiers.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec control for verifying SSH security configuration. Will need to be converted to Ansible assertions or Molecule verifiers.
- `chef-and-ansible/index.html`: Sample HTML file for testing web server functionality.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in assert module or Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Vagrant**: Can continue to be used with Molecule for local testing

### Security Considerations

- **SSL Certificate Management**: The current solution generates self-signed certificates. Migration should maintain this capability using Ansible's `openssl_*` modules.
- **SSL Protocol Configuration**: The poodle_fix playbook addresses SSL vulnerabilities by restricting protocols. This security hardening must be preserved.
- **SSH Security Controls**: The ssh_profile.rb InSpec test verifies SSH security configurations that must be maintained in the migrated solution.
- **Hardcoded Credentials**: The setup scripts contain hardcoded usernames and passwords that should be moved to Ansible Vault or another secrets management solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates in website_https.yml

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods may require additional validation steps.
- **Chef Automate/Server Setup**: Converting the Chef server setup scripts to Ansible will require knowledge of Chef server installation requirements and configuration options.
- **Security Compliance**: Ensuring that the security controls verified by InSpec are properly implemented and tested in the Ansible solution.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Minimal changes needed, mainly updating to current Ansible best practices
   - Convert InSpec tests to Ansible assertions or Molecule verifiers

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Minimal changes needed, mainly updating to current Ansible best practices
   - Convert InSpec tests to Ansible assertions or Molecule verifiers

3. **Chef server setup scripts** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management for credentials

### Assumptions

1. The current Ansible playbooks are functional and represent the desired end state for the migrated solution.
2. The Chef InSpec tests accurately verify the required functionality and security posture.
3. The Chef Automate and Chef Infra Server setup scripts are still relevant and need to be converted to Ansible.
4. No additional Chef cookbooks or resources are being used beyond what's visible in the repository.
5. The target environment will continue to be Ubuntu 20.04 or compatible systems.
6. The migration does not require changes to the underlying application functionality, only to the deployment and testing methods.
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with proper secret management in the migrated solution.