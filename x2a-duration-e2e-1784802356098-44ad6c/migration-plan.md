# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, consisting primarily of Ansible playbooks for configuring web servers with SSL and Chef InSpec tests for validation. There are also Chef Automate and Chef Infra Server deployment scripts. The estimated timeline for migration is 1-2 weeks given the limited scope and straightforward configurations.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with SSL/TLS support
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative configuration management solution

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
- **Self-signed Certificates**: The current implementation generates self-signed certificates; consider using Let's Encrypt or other certificate management solutions
- **SSH Hardening**: The InSpec tests verify SSH security configurations that must be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use secure key management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks will require careful mapping of test assertions
- **Chef Server Replacement**: If Chef Server functionality is needed, determine appropriate Ansible inventory and variable management approaches
- **Compliance Validation**: Ensuring that compliance checks currently performed by InSpec are properly implemented in the Ansible ecosystem

### Migration Order

1. **website-https playbook** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle-fix playbook** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec tests** (moderate complexity): Convert to Ansible-compatible testing framework
4. **Chef deployment scripts** (high complexity): Replace with Ansible roles for configuration management platform deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than production deployment
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only
3. The self-signed certificates are acceptable for the demonstration environment
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. There is no complex state management or data persistence requirements
6. The migration will maintain the same level of security compliance validation
7. Test Kitchen can be fully replaced by Ansible Molecule or similar testing framework
8. The Chef Automate and Chef Infra Server deployment may not be needed in the Ansible-only environment