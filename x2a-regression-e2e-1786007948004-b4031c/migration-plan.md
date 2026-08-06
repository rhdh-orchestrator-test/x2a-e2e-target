# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer. The primary challenge will be replacing Chef Automate/Infra Server functionality with appropriate Ansible alternatives while maintaining compliance testing capabilities.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

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

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for validating HTTPS configuration and security

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for web UI, role-based access control, and job scheduling
- **Chef InSpec**: Maintain as-is for compliance testing or migrate to Ansible's built-in assert module combined with community modules for compliance checks
- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols. This security hardening should be preserved in the migrated solution.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate Ansible-based solution to replace Chef Automate's functionality (AWX/Tower or alternative)
- **InSpec Integration**: Ensuring continued compliance testing capability, either by maintaining InSpec or implementing equivalent Ansible-based testing
- **User/Organization Management**: Replicating Chef's user and organization management in an Ansible-based solution

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, only need standardization
2. **InSpec Tests**: Moderate complexity, decide whether to maintain as-is or convert to Ansible-native testing
3. **Chef Deployment Scripts**: High complexity, requires designing an Ansible-based replacement for Chef Automate/Infra Server

### Assumptions

1. The primary use case for Chef in this repository is for server deployment and management, not for extensive configuration management across a large fleet
2. InSpec is being used primarily for compliance testing of Ansible-managed infrastructure
3. The Test Kitchen setup is for development/testing only and not part of production workflows
4. The hardcoded credentials in the deployment scripts are examples and not used in production
5. The repository is primarily educational/demonstrative and not a production infrastructure codebase
6. The Apache configuration is a simple example and not representative of complex production configurations
7. The migration goal is to standardize on Ansible while maintaining compliance testing capabilities