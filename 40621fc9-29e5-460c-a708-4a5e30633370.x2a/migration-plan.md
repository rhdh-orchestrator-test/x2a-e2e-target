# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of Chef Automate and Chef Infra Server deployment scripts, along with some existing Ansible playbooks for web server configuration and compliance testing using Chef InSpec. The estimated timeline for migration is 1-2 weeks given the limited scope and existing Ansible components.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts using Chef deployment tools
    - Key Features: User creation, organization setup, server configuration

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring Apache web server with HTTPS and fixing SSL vulnerabilities
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup, POODLE vulnerability fix

- **chef-and-ansible/tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port testing, SSL protocol verification, SSH configuration checks

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server deployment
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Can be retained as a compliance testing tool and integrated with Ansible workflows

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL configuration for Apache web servers
  - Migration approach: Maintain the same security settings in Ansible playbooks
  
- **SSH Security Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Ensure Ansible playbooks enforce the same SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificates generated during deployment
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: The current deployment uses Chef-specific CLI tools
  - Mitigation: Create Ansible roles that install and configure equivalent monitoring and compliance tools

- **InSpec Integration**: The current setup uses InSpec for compliance testing
  - Mitigation: Maintain InSpec for testing or migrate to Ansible-native solutions like ansible-lint or molecule

### Migration Order

1. **chef-and-ansible** (already in Ansible format, low risk)
2. **setup-automate** (high complexity, requires replacement of Chef-specific functionality)
3. **chef-and-ansible/tests** (moderate complexity, may require adaptation of InSpec tests or replacement with Ansible-native testing)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef deployment scripts are used for setting up test environments
3. The hardcoded credentials in the deployment scripts are not used in production environments
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for local development and testing
6. The compliance requirements enforced by InSpec tests will remain the same after migration