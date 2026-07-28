# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests for compliance validation
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure automation into Ansible.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Convert InSpec tests to Ansible-native testing with:
  - ansible-lint for static analysis
  - ansible-test for integration testing
  - Consider keeping InSpec for compliance testing or migrate to ansible-compliance

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 enforcement and disabled SSL3
  - Approach: Use Ansible's `lineinfile` or `template` module with identical configuration
  
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Approach: Create equivalent Ansible tasks to enforce SSH hardening and verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use ansible-test or maintain InSpec as a compliance tool alongside Ansible
  
- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible automation
  - Mitigation: Create Ansible roles for deploying alternative compliance and automation tools

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Add proper variable handling and templating
   
2. **poodle-fix playbook** (low risk, already Ansible)
   - Integrate with website-https as a single role
   - Implement idempotent configuration management
   
3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible testing framework or maintain as compliance tool
   - Ensure all compliance checks are preserved
   
4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible roles for deploying alternative compliance tools
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec alongside Ansible for compliance automation
2. The Chef deployment scripts are used for setting up a test environment
3. There are no external dependencies or integrations not visible in the repository
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No actual application code or complex business logic needs migration
6. The InSpec tests are critical for compliance validation and must be preserved in functionality
7. No CI/CD pipeline integration is present in the current repository