# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for configuring a secure web server. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Sample HTML file used in the web server configuration

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible workflow

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipeline configurations

### Security Considerations

- **SSL/TLS Configuration**: Maintain the security hardening that disables SSLv3 and enables TLSv1.2
- **Self-signed Certificates**: Consider integrating with Ansible Vault for certificate management or using Let's Encrypt for production environments
- **SSH Security Controls**: Ensure SSH hardening controls are maintained in the Ansible configuration
- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities may require additional modules or external tools
- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references) that needs to be preserved in documentation or comments
- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible roles for configuration management infrastructure

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Already in Ansible format, just need review and optimization
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are intended to validate the Ansible configurations
3. There are no external Chef cookbooks or complex Chef-specific resources being used
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex state management or data bags are in use
6. The deployment scripts are for setting up a test environment rather than production infrastructure