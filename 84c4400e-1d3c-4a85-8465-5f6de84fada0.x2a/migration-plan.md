# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting of two Ansible playbooks for web server configuration and two bash scripts for Chef server/Automate deployment. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be directly reused) and medium complexity for converting the Chef server deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with SSL/TLS setup, including self-signed certificate generation and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for the POODLE vulnerability in SSL by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management system
- **InSpec**: Can be retained as a testing framework, even with Ansible (as demonstrated in the existing setup)

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Migration approach: Direct reuse of existing Ansible playbook
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Direct reuse of existing Ansible playbook or consider enhancing with Let's Encrypt integration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

- **SSH Security**: The InSpec profile enforces SSH root login restrictions
  - Migration approach: Create an Ansible role that applies the same SSH hardening rules and is tested with the existing InSpec profile

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform the same system configuration and package installation
  
- **InSpec Integration**: Ensuring continued compliance testing with InSpec
  - Mitigation: Maintain the existing InSpec tests and integrate them into the Ansible workflow

- **Configuration Management Transition**: Moving from Chef-based configuration management to Ansible-only
  - Mitigation: Document the transition process and provide training for team members

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, can be directly reused
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Low risk, can be directly reused with Ansible
3. **Chef Server Deployment** (deploy-chef-server.sh) - Medium complexity, requires conversion to Ansible roles
4. **Chef Automate Deployment** (deploy-automate.sh) - Medium complexity, requires conversion to Ansible roles or replacement with alternative solution

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and can be directly reused
2. The InSpec tests will continue to be used for compliance verification with Ansible
3. The Chef server and Automate deployment will be replaced with an Ansible-based configuration management solution
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The migration will maintain the same level of security hardening and compliance testing
6. No application-specific configurations beyond web server setup are present in the repository
7. The team has experience with both Chef and Ansible, facilitating the transition