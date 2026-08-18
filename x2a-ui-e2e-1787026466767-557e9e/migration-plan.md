# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and integrating the Chef InSpec testing capabilities into Ansible's testing framework. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configurations

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Convert InSpec tests to Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in assert module for basic tests
  - Option 2: Integrate with Molecule's verifier using Testinfra
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Chef Automate/Server Deployment**: Convert bash scripts to Ansible roles for:
  - Chef Automate installation
  - Chef Server installation
  - User and organization management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL protocol restrictions
  
- **SSH Hardening**: The InSpec test checks for SSH root login restrictions
  - Approach: Create an Ansible role for SSH hardening that implements the security controls tested by the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
    - Migrate to Ansible Vault for secure credential storage
  - Self-signed certificates in website_https.yml
    - Use Ansible Vault or integrate with external certificate management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Molecule with Testinfra or maintain InSpec as a separate testing tool
  
- **Chef Automate/Server Deployment**: Converting the bash scripts to idempotent Ansible roles
  - Mitigation: Break down the installation steps into discrete tasks with proper state checking

- **SSL Certificate Management**: Ensuring proper handling of SSL certificates
  - Mitigation: Use Ansible's crypto modules for certificate generation and management

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Restructure into Ansible role format
   - Add proper variable management
   - Implement idempotency improvements

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Integrate with the website_https role as a security enhancement
   - Implement as a separate task file within the Apache role

3. **InSpec Tests** (moderate complexity)
   - Set up Molecule testing framework
   - Convert InSpec tests to equivalent assertions in Molecule/Testinfra

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement secure credential management with Ansible Vault
   - Add proper error handling and idempotency checks

### Assumptions

1. The current Ansible playbooks are functional but may not follow best practices for structure and organization
2. The InSpec tests are used for compliance validation and should be preserved in some form
3. The Chef deployment scripts are used for setting up infrastructure and could be replaced with Ansible equivalents
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration will maintain the same functionality but improve structure and maintainability
7. No specific CI/CD pipeline integration requirements are specified
8. The Apache web server configuration is relatively standard and doesn't have custom modules or configurations beyond what's shown