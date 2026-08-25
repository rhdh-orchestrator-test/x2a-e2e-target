# MIGRATION FROM ANSIBLE AND CHEF SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef server deployment scripts that need to be migrated to a standardized Ansible structure. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration scope is relatively small, consisting of two Ansible playbooks for web server configuration and two bash scripts for Chef server/Automate deployment. The estimated timeline for migration is 1-2 days given the limited scope and straightforward nature of the existing code.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying the HTTPS website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (for testing), but deployment scripts suggest they could be used on any VM
- **Cloud Platform**: Not specified, but scripts appear to be designed for both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management solution
- **Test Kitchen with Ansible**: Migrate to Molecule for Ansible role testing
- **InSpec Tests**: Convert to Ansible Molecule verifiers or maintain as standalone tests

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. This should be preserved in the migrated Ansible roles.
- **POODLE Vulnerability Fix**: The security hardening in poodle_fix.yml should be incorporated into the main Apache role.
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be replaced with Ansible Vault:
  - Username/password combinations in deploy-automate.sh and deploy-chef-server.sh
  - Consider using lookup plugins or external secret management

### Technical Challenges

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality
  - Mitigation: Consider Ansible AWX/Tower for web UI, inventory management, and job scheduling
  
- **InSpec Integration**: Maintaining compliance testing capabilities currently provided by InSpec
  - Mitigation: Integrate InSpec tests with Ansible workflows or migrate to Ansible-native testing tools

### Migration Order

1. **website_https.yml** (Priority 1): Convert to an Ansible role with proper variable structure
2. **poodle_fix.yml** (Priority 1): Incorporate into the Apache role as a security hardening task
3. **Chef Deployment Scripts** (Priority 2): Convert to Ansible playbooks for infrastructure deployment

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The InSpec tests are intended to be run as part of a CI/CD pipeline
3. The Chef deployment scripts are meant to be run on a fresh VM
4. No external Chef cookbooks or complex Chef-specific features are being used
5. The target environment will continue to be Ubuntu-based systems
6. There is no requirement to maintain backward compatibility with Chef
7. The migration will standardize on Ansible as the sole configuration management tool