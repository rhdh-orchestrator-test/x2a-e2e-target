# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need to be migrated to a unified Ansible solution. The repository appears to be a collection of examples demonstrating Chef InSpec with Ansible for compliance automation, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to convert. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec profile to verify SSH security compliance
- `index.html`: Simple HTML file for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX (open-source version of Ansible Tower)

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the Apache SSL configuration
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to configure Apache SSL settings
  
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **InSpec Tests**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible's assert module or integrate with Molecule for testing
  
- **Chef-specific Functionality**: Replacing Chef Automate and Chef Infra Server with Ansible equivalents
  - Mitigation: Use Ansible Automation Platform or AWX for similar functionality

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires replacement of Chef-specific functionality)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The migration will replace Chef Automate/Infra Server with Ansible Automation Platform or AWX
3. The InSpec compliance tests will need to be converted to equivalent Ansible verification methods
4. The self-signed SSL certificates are acceptable for the migrated solution
5. The hardcoded credentials in the deployment scripts will be replaced with secure alternatives
6. The Apache configuration and website deployment will remain functionally equivalent