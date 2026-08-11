# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks used for demonstration purposes. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance automation. The repository is relatively small and contains:

1. Chef Automate and Chef Server deployment scripts
2. Ansible playbooks for configuring a web server with HTTPS
3. InSpec tests for verifying the web server configuration

The migration complexity is low to medium, as most of the content is already in Ansible format or consists of shell scripts that can be converted to Ansible roles. The estimated timeline for migration would be 1-2 weeks for a single developer, focusing on converting the Chef server deployment scripts to Ansible roles and ensuring the InSpec tests continue to work with the new deployment method.

## Module Migration Plan

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Server deployment, user and organization creation

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-ssl-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain or migrate to Molecule for Ansible role testing
- **InSpec**: Can be maintained as is, as it works well with Ansible for compliance testing

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Maintain the same security configurations in the Ansible roles
- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible roles
  - Mitigation: Create dedicated Ansible roles for Chef server deployment with appropriate variables
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new deployment method
  - Mitigation: Maintain the same output structure and verification points in the new Ansible roles

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible format)
2. **poodle-ssl-fix** (low risk, already in Ansible format)
3. **chef-automate-deployment** (moderate complexity, requires conversion from Bash to Ansible)

### Assumptions

1. The repository is primarily for demonstration purposes and not for production use
2. The InSpec tests are intended to be maintained as part of the compliance automation strategy
3. The Chef server deployment scripts are intended to be converted to Ansible roles
4. The hardcoded credentials in the setup scripts are for demonstration purposes only
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. The migration will maintain the same functionality and security configurations
7. The repository is not actively used in production environments
8. The primary goal is to standardize on Ansible for infrastructure automation while maintaining InSpec for compliance testing