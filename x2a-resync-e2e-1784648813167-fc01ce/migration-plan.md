# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate infrastructure configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, as indicated by the README in the chef-and-ansible directory.

The migration scope is relatively small, consisting of:
- 2 Ansible playbooks for configuring web servers with HTTPS
- 2 Chef InSpec test files for validating configurations
- 2 Shell scripts for deploying Chef Automate and Chef Infra Server

The estimated timeline for migration is 1-2 weeks, with low complexity since most of the infrastructure code is already in Ansible format. The main work will be converting the Chef InSpec tests to Ansible-native testing solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified all paths using `list_directory` and `file_search` tools. The repository does not contain any traditional Chef cookbooks with recipes/default.rb files, Puppet modules with manifests/init.pp files, or PowerShell modules with .psd1 files. Instead, it contains Ansible playbooks, Chef InSpec tests, and shell scripts as detailed below.

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test that validates HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (STIG)

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/index.html`: Sample HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible Assert module for in-playbook validation
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for test orchestration
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Ensure SSLv3 is disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible
  - Disable root login via SSH
  - Implement the STIG compliance requirements

- **Vault/secrets management**:
  - The current implementation has hardcoded passwords in the Chef server deployment scripts
  - Recommendation: Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Test Conversion**: Converting Chef InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Challenge: InSpec has domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with appropriate conditions or maintain InSpec as a separate tool

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Challenge: Ansible doesn't have built-in compliance reporting
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or maintain InSpec for this purpose

### Migration Order

1. **website-https.yml** (Priority 1): Already in Ansible format, minimal changes needed
2. **poodle_fix.yml** (Priority 1): Already in Ansible format, minimal changes needed
3. **Chef InSpec Tests** (Priority 2): Convert to Ansible testing framework
4. **Chef Deployment Scripts** (Priority 3): Replace with Ansible roles for infrastructure management

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies where possible
2. The InSpec tests are valuable and their functionality should be preserved in some form
3. The deployment scripts for Chef Automate and Chef Server may be deprecated entirely if Chef is no longer used
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security requirements expressed in the InSpec tests must be maintained in the Ansible implementation