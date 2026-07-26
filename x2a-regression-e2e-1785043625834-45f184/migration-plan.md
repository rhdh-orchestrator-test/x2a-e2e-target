# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec and Ansible configurations that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all configuration management into Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-compliance**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **ssh-compliance**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security checks, CCI compliance mapping, STIG references

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Template for the Hello World website content
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's built-in `assert` module for basic tests
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific CI/CD pipeline configurations

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for SSL hardening that can be applied consistently
  - Ensure the role includes the same TLS protocol restrictions (disabling SSLv3, enabling TLSv1.2)

- **Compliance Testing**: The InSpec tests contain important security checks that must be preserved
  - Approach: Convert InSpec tests to Ansible assert statements or Molecule tests
  - Ensure STIG and CCI compliance references are maintained in documentation

- **Vault/secrets management**:
  - No explicit secrets management was detected in the current codebase
  - Hardcoded credentials were found in the Chef deployment scripts (username, password)
  - Migration should implement Ansible Vault for securing these credentials

### Technical Challenges

- **Compliance Testing Migration**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Create a mapping between InSpec resources and Ansible modules
  - Consider maintaining InSpec as a standalone tool if direct conversion is too complex

- **Self-signed Certificate Generation**: Ensuring the certificate generation process is properly migrated
  - Mitigation: Use Ansible's `openssl_*` modules which are already in use in the current playbooks

- **Test Kitchen to Molecule Migration**: Ensuring test environments are properly configured
  - Mitigation: Create equivalent Molecule scenarios for each Test Kitchen suite

### Migration Order

1. **website-https** (low risk, already in Ansible)
   - Create an Ansible role structure for the website configuration
   - Move the existing playbook tasks into appropriate role files

2. **poodle-fix** (low risk, already in Ansible)
   - Create an Ansible role for SSL hardening
   - Move the existing playbook tasks into the role

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assert statements or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
2. Compliance testing is a critical requirement that must be preserved in the migration
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible automation
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external data sources or inventory systems are in use that would need migration
6. The migration will maintain the same level of security hardening present in the original code
7. No application-specific configurations beyond the web server setup are present