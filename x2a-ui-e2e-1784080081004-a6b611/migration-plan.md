# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec test profiles that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate/Chef Server deployment scripts that need to be converted to Ansible playbooks

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks for a single developer, as the repository primarily contains examples rather than production infrastructure code.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Use ansible-lint for static analysis of playbooks
  - Option 3: Implement pytest-ansible for Python-based testing of Ansible-managed infrastructure

- **Test Kitchen**: Replace with:
  - Ansible Molecule for a complete testing framework
  - Or continue using Test Kitchen with the ansible provisioner if preferred

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that:
  - Install and configure equivalent compliance and automation tools
  - Options include:
    - AWX/Ansible Tower for automation
    - Compliance tools like OpenSCAP or OSCAP Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enforced
  - Disable insecure protocols

- **SSH Hardening**: Maintain the SSH security controls verified by the InSpec profile
  - Ensure root login remains disabled
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to an Ansible-compatible testing framework
  - Mitigation: Use Ansible assert modules or Molecule verifiers to implement equivalent tests
  - Consider maintaining InSpec as a testing tool even with Ansible if the team has expertise

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality
  - Mitigation: Evaluate AWX/Tower for GUI and API-driven automation
  - Consider simpler Git-based approaches if full Chef Server functionality isn't required

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and need minimal changes
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible Molecule or equivalent testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create Ansible playbooks for equivalent functionality

### Assumptions

1. The repository is primarily for demonstration purposes rather than production infrastructure
2. The team is comfortable with Ansible but wants to migrate away from Chef InSpec testing
3. The security compliance requirements (STIG references in ssh_profile.rb) must be maintained in the Ansible implementation
4. The deployment scripts are used for setting up test environments rather than production Chef infrastructure
5. No external data sources or complex integrations are present in the current implementation
6. The migration is focused on technical implementation rather than changing the underlying security or configuration requirements