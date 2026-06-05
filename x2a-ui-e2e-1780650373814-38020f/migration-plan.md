# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring a web server with HTTPS
2. Chef InSpec tests for validating the security and functionality of the deployed configuration

Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server that will need to be converted to Ansible playbooks.

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single developer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2, restarts Apache and SSH services

- **website-https-verification**:
    - Description: Chef InSpec test that verifies the HTTPS website is properly configured and running
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-security-profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
  - Migration strategy: Convert InSpec tests to Ansible assert tasks or Molecule verify tests
  - Alternative: Keep InSpec as a testing tool but integrate it with Ansible workflows

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Migration strategy: Create equivalent Molecule configuration for testing Ansible roles

- **Apache 2.4.41**: Maintain the same version requirement in Ansible playbooks
  - Migration strategy: Use Ansible's package module with version specification

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Migration approach: Ensure the Ansible templates for Apache configuration maintain the same security settings

- **SSH Security**: The SSH root login restriction must be maintained
  - Migration approach: Include SSH configuration in the Ansible roles with appropriate security settings

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Migration approach: Maintain the same approach or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's native testing capabilities
  - Mitigation strategy: Use Ansible's assert module for basic tests and consider keeping InSpec for complex compliance testing

- **Maintaining Compliance Standards**: The current InSpec tests include STIG compliance checks
  - Mitigation strategy: Ensure compliance metadata is preserved in documentation or use Ansible roles specifically designed for compliance

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation strategy: Create an Ansible role that performs the same steps as the bash scripts, ensuring idempotence

### Migration Order

1. **website-https** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Add documentation and improve variable naming

2. **poodle-fix** (low risk, already Ansible)
   - Integrate into the website-https role as a security configuration option

3. **InSpec Tests** (medium complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Maintain compliance metadata

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The current implementation is used for testing and demonstration purposes, not production
2. The self-signed certificates are acceptable for the use case
3. The hardcoded credentials in the deployment scripts are for demonstration only
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. There is no requirement to maintain backward compatibility with Chef InSpec
6. The migration is primarily focused on standardizing on Ansible rather than addressing functional gaps
7. The current Test Kitchen setup is used for development and testing, not for production deployment