# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Two Ansible playbooks for configuring HTTPS websites with proper SSL/TLS security
2. Two bash scripts for deploying Chef Automate and Chef Infra Server
3. Chef InSpec tests for verifying HTTPS configuration

The migration complexity is **LOW** with an estimated timeline of **1-2 DAYS** to complete. The primary work involves consolidating the existing Ansible playbooks and replacing the Chef Automate/Infra Server deployment scripts with equivalent Ansible roles.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS, generates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but call it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or simplify to use Vagrant directly with Ansible provisioner

### Security Considerations

- **SSL/TLS Configuration**: The playbooks properly configure TLS 1.2 and disable older protocols
  - Migration approach: Maintain the same security hardening in the consolidated Ansible roles
  
- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Consider enhancing with Let's Encrypt integration for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate/Server Deployment**: Converting the Chef deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts
  - Consider using the official Chef Automate Ansible Collection if available

- **InSpec Testing**: Replacing InSpec tests with Ansible-native testing
  - Mitigation: Use Ansible's assert module or Molecule for testing
  - Alternative: Keep InSpec and call it from Ansible if the team is familiar with InSpec

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Refactor into a proper Ansible role structure
   - Update testing framework

2. **poodle-fix playbook** (low risk, already Ansible)
   - Integrate into the website-https role as a security hardening task
   - Update testing framework

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. The Chef InSpec tests are used for compliance verification of the Ansible-deployed infrastructure
3. The hardcoded credentials in the deployment scripts are for demonstration only
4. The target environment is Ubuntu 20.04 as specified in the Test Kitchen configuration
5. The Apache configuration is basic and doesn't include complex customizations
6. The self-signed certificates are acceptable for the use case (not production)
7. The Chef Automate and Chef Server deployment is for demonstration/lab environments