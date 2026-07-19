# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks and ensuring the existing Ansible playbooks follow best practices. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that most configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks for Apache HTTPS configuration and InSpec tests
    - Path: chef-and-ansible
    - Technology: Ansible/Chef InSpec
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup, security testing

- **tests**:
    - Description: InSpec tests for verifying HTTPS functionality and SSH security configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks, SSH security compliance

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS
- `poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability
- `deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks
- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing
- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks

### Security Considerations

- **SSL Configuration**: Maintain TLSv1.2 enforcement and disable insecure protocols
- **SSH Security**: Maintain SSH security controls from the InSpec profile
- **Vault/secrets management**: Migrate hardcoded credentials to Ansible Vault

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing
- **Compliance Reporting**: Maintaining compliance reporting capabilities
- **Chef Server Deployment**: Replacing Chef server deployment with Ansible alternatives

### Migration Order

1. **chef-and-ansible** (low risk, already contains Ansible playbooks)
2. **tests** (moderate complexity)
3. **setup-automate** (high complexity)

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The organization is willing to replace Chef InSpec with Ansible-native testing solutions
4. The hardcoded credentials in the setup scripts are for demonstration purposes only