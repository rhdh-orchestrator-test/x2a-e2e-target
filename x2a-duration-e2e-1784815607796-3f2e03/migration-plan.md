# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating the Ansible configurations and SSH security
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on creating Ansible equivalents for the Chef server deployment scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef components that need individual migration planning:

### MODULE INVENTORY

Note: No traditional Puppet modules (with manifests/init.pp), Chef cookbooks (with recipes/default.rb), or PowerShell modules (.psd1) were found in the repository. The following components were identified:

- **website_https**:
    - Description: Ansible playbook for configuring Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test for validating HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec test for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, security compliance checks with STIG references

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the Ansible provisioner (already in use)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Semaphore for lightweight UI

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Proper SSL protocol settings (TLS 1.2 enforcement)
  - Disabling of vulnerable protocols (SSL3)

- **SSH Security**: The InSpec tests validate SSH security configurations:
  - Root login restrictions
  - STIG compliance requirements
  - Migration should include equivalent Ansible checks

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials:
  - In deploy-automate.sh and deploy-chef-server.sh: username, password, email
  - Migration should use Ansible Vault for securing these credentials

- **Certificate Management**: Current implementation uses OpenSSL for certificate generation
  - Migration should use Ansible's crypto modules for certificate management
  - Consider integration with certificate management systems for production environments

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-compatible testing
  - Challenge: InSpec has specific syntax for infrastructure testing
  - Mitigation: Use Ansible Molecule with Testinfra or Goss for similar functionality
  - Special attention needed for STIG compliance checks in ssh_profile.rb

- **Chef Server Functionality**: Replacing Chef Server/Automate functionality
  - Challenge: Chef Server provides specific features for node management and policy application
  - Mitigation: Implement equivalent functionality using Ansible AWX/Tower or alternative tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml)
   - Low risk as they're already in Ansible format
   - May need minor updates to follow current Ansible best practices
   - Update module syntax for newer Ansible versions if needed

2. **Testing Framework** (website_https_verify.rb, ssh_profile.rb)
   - Convert InSpec tests to Ansible Molecule or equivalent
   - Ensure all current test cases are covered in the new framework
   - Maintain compliance metadata from ssh_profile.rb

3. **Chef Server Deployment** (deploy-automate.sh, deploy-chef-server.sh)
   - Create Ansible playbooks to replace the bash scripts
   - Implement secure credential management with Ansible Vault
   - Set up equivalent user and organization management in Ansible AWX/Tower

### Assumptions

1. The current implementation uses Test Kitchen primarily for testing Ansible playbooks, not for Chef cookbook development
2. The Chef InSpec tests are used for validation only and don't have dependencies on Chef Infra Client
3. The deployment scripts are used for setting up infrastructure, not for ongoing configuration management
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The SSL configuration requirements (TLS 1.2, disabled SSL3) will remain the same
6. The Apache configuration details (virtual hosts, document roots) will remain consistent
7. The SSH security requirements specified in the InSpec tests will need to be maintained
8. There are no external dependencies or integrations not visible in the provided files
9. The migration will not require changes to the underlying application architecture