# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with Ansible verifier
- **InSpec**: Can be maintained as a testing tool, even in an Ansible-only environment

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Migration approach: Preserve the existing Ansible task that sets SSLProtocol to disable weak protocols
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Maintain the existing Ansible OpenSSL module usage or consider using Ansible Vault for certificate storage

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that satisfies the InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same system configuration and package installation
  
- **InSpec Integration**: Maintaining InSpec tests in an Ansible-only workflow
  - Mitigation: Use Ansible's built-in testing capabilities or continue using InSpec as a standalone testing tool

- **Test Kitchen**: Replacing or adapting Test Kitchen for Ansible-only testing
  - Mitigation: Migrate to Ansible Molecule for testing or maintain Test Kitchen with Ansible verifier

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Ensure idempotence and best practices

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Determine whether to maintain InSpec or convert to Ansible testing
   - If converting, create equivalent Ansible assertions

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential storage

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are valuable and should be maintained in some form
3. The Chef Automate and Chef Server deployment scripts are intended for actual use
4. The hardcoded credentials in the deployment scripts are placeholders and not actual credentials
5. The target environment is Ubuntu 20.04 as specified in kitchen.yml
6. The existing Ansible playbooks are functional and follow best practices
7. There are no external dependencies or requirements not visible in the repository