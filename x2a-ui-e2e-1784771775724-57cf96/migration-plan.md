# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with both Chef InSpec tests and Ansible playbooks. The primary focus appears to be on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The repository includes Ansible playbooks for configuring web servers with HTTPS, Chef InSpec tests for verification, and scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no Puppet modules (no manifests/init.pp files), no Chef cookbooks (no recipes/default.rb files), and no PowerShell modules (no .psd1 files) in this repository. The repository primarily contains Ansible playbooks and Chef InSpec tests.

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_ssh_profile**:
    - Description: Chef InSpec test for verifying SSH configuration security
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **inspec_website_https**:
    - Description: Chef InSpec test for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS port verification, SSL protocol verification, website content verification

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef server deployment, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Sample HTML file for website testing. Migration consideration: Can be used as-is or converted to a template.
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples. Migration consideration: Update to reflect the new Ansible-only approach.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Keep InSpec as a standalone testing tool that can be called from Ansible

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Apache2 (2.4.41-4ubuntu3.10)**: Continue using the apache2 module in Ansible

- **OpenSSL**: Continue using the openssl_* modules in Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache to use TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.
  - Migration approach: Use the same configuration parameters in the Ansible apache2_module and apache2_conf modules

- **SSH Hardening**: The InSpec tests verify that SSH root login is disabled.
  - Migration approach: Create an Ansible playbook that configures SSH according to security best practices and verifies the configuration

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Continue using Ansible's openssl_* modules for certificate generation, but consider adding support for Let's Encrypt for production environments

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation strategy: Create equivalent tests using Ansible's assert module or Molecule verify phase

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible playbooks.
  - Mitigation strategy: If Chef server is still needed, create Ansible playbooks that install and configure Chef server; if not, remove these components entirely

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires decision on whether to keep Chef components)

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. The InSpec tests are valuable and should be preserved in some form
3. The Chef server deployment scripts may no longer be needed if fully migrating to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (TLS 1.2, SSH hardening) will remain the same
7. The self-signed certificates approach is acceptable, but may need enhancement for production