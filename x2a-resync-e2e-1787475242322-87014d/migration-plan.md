# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles
- **Chef InSpec**: Two options:
  1. Convert InSpec tests to Ansible assertions using assert module
  2. Maintain InSpec tests but integrate them into Ansible workflow using the `community.general.inspec` module
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source Ansible AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible roles.
  - Migration approach: Create an Ansible role for SSL certificate management with proper secret handling
  
- **SSH Hardening**: InSpec tests verify SSH security configurations.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions or maintaining InSpec integration
  - Mitigation: Use the `community.general.inspec` module to run existing InSpec tests from Ansible
  
- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality
  - Mitigation: Evaluate Ansible Automation Platform or AWX as alternatives, focusing on the specific features used

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Add documentation
   
2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Add documentation
   
3. **InSpec tests** (moderate complexity)
   - Either convert to Ansible assertions or integrate with Ansible using community.general.inspec
   
4. **Chef Automate/Server deployment scripts** (high complexity)
   - Convert to Ansible roles for infrastructure deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Compliance testing is still a requirement, but can be implemented in Ansible or by calling InSpec from Ansible
3. The deployment scripts for Chef Automate/Server will be replaced with equivalent Ansible roles
4. The target environment will remain Ubuntu 20.04 or similar Linux distributions
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data structures or external data sources are being used
8. The security requirements represented in the InSpec tests must be maintained