# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with both Chef and Ansible components. The primary focus appears to be on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository includes Ansible playbooks for configuring web servers with HTTPS, Chef InSpec tests for verifying configurations, and bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for migration would be approximately 1-2 weeks, with low complexity as most components are already in Ansible format or can be easily converted to pure Ansible solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using a self-signed certificate
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Checks SSH configuration for security compliance

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Verifies port 443 is listening, website returns 200 status, SSL/TLS protocols are properly configured

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Configures hostname, system settings, downloads and deploys Chef Automate, creates users and organizations

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Similar to deploy-automate.sh but only deploys Chef Infra Server

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used as a template for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and control
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. This should be maintained or enhanced in the Ansible migration.
  - Migration approach: Use the Ansible `lineinfile` or `template` module to configure Apache SSL settings

- **SSH Security**: The InSpec test verifies that SSH root login is disabled.
  - Migration approach: Create an Ansible task to ensure this configuration is applied and verified

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or Molecule tests.
  - Mitigation: Create equivalent checks using Ansible's assert module or custom modules

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible equivalents.
  - Mitigation: Create Ansible roles for AWX/Tower deployment or use the official Ansible Automation Platform installer

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec tests** (convert to Ansible assertions or Molecule tests, moderate complexity)
4. **Chef deployment scripts** (convert to Ansible roles for AWX/Tower deployment, higher complexity)

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality
2. The InSpec tests are used for validation and compliance checking, not for configuration management
3. The deployment scripts are used for setting up Chef infrastructure, which would be replaced by Ansible infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The security requirements (TLS 1.2, SSH configuration) will remain the same
6. The self-signed certificates are acceptable for the use case, or can be replaced with proper certificates
7. The current Ansible playbooks (website_https.yml, poodle_fix.yml) are working as expected and can be used as-is
8. Test Kitchen is only used for development/testing and not in production environments