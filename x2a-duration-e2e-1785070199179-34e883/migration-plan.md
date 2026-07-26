# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing files and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The main effort will be in replacing Chef InSpec tests with Ansible-native testing solutions.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and SSL security settings
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Used for local testing and validation.
- `index.html`: Simple HTML file used as a test page for the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified as the driver in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the Ansible `assert` module for basic testing
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing and development
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure provisioning
  - Consider migrating to Ansible Tower/AWX for enterprise orchestration

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or enhance:
  - Self-signed certificate generation (currently using openssl_* modules)
  - TLS protocol restrictions (disabling older protocols)
  - Virtual host SSL configuration

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled in Ansible-managed configurations
  - Maintain compliance with security standards referenced in tests (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - The current repository contains hardcoded credentials in the Chef deployment scripts
  - Migration should implement Ansible Vault for securing:
    - User passwords (currently hardcoded as 'password')
    - Any other sensitive information

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing:
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use a combination of Ansible assert, custom modules, and external testing frameworks

- **Deployment Script Conversion**: Converting Chef deployment scripts to Ansible:
  - Challenge: Chef Automate has specific deployment requirements
  - Mitigation: Research Ansible roles for Chef deployment or create custom roles

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk as these are already in Ansible format
   - Focus on optimizing, modularizing into roles, and implementing best practices

2. **Test Framework** (InSpec tests):
   - Moderate complexity
   - Convert to Ansible-native testing solutions
   - Ensure all compliance checks are maintained

3. **Deployment Scripts**:
   - Higher complexity
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management

### Assumptions

1. The repository is primarily educational/demonstrational and not a production system
2. The InSpec tests are used for validating the Ansible configurations, not as part of a larger compliance framework
3. The deployment scripts are examples and not used for critical infrastructure
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. No CI/CD pipeline integration is currently implemented
7. The migration will maintain the same functionality but using pure Ansible solutions