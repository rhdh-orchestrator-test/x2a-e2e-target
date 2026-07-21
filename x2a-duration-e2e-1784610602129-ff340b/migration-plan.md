# MIGRATION FROM CHEF AUTOMATE/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a hybrid infrastructure with Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is moderate, focusing on two main components:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Replacing Chef InSpec tests with Ansible-native testing solutions

The repository is relatively small with only a few components, suggesting a migration timeline of 1-2 weeks for a single developer or 3-5 days for a small team.

## Module Migration Plan

This repository contains a mix of Bash scripts for Chef deployment and Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for configuring Apache with HTTPS and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, disabling SSLv3

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **inspec-https-verification**:
    - Description: Chef InSpec tests for HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration will require replacing with Ansible-native testing framework like Molecule.
- `chef-and-ansible/index.html`: Sample HTML file used for testing the web server. Can be reused as-is in the Ansible migration.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml and Apache package version 2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible playbooks that install and configure equivalent monitoring/compliance solutions
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Replace with ansible-lint or OpenSCAP integration
  - For infrastructure testing: Replace with Molecule or Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in the poodle_fix.yml playbook
  - Migration approach: Preserve the same Apache SSL configuration settings in the Ansible playbooks
  
- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Migration approach: Use the same Ansible openssl modules or consider integrating with Let's Encrypt for production environments

- **SSH Security**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Implement equivalent checks using Ansible's assert module or ansible-lint

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password, email)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require finding equivalent functionality
  - Mitigation: Use Ansible's assert module for basic tests and consider ansible-lint or OpenSCAP for compliance testing

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced
  - Mitigation: Map Chef Automate features to equivalent Ansible solutions (AWX/Tower for web UI, ansible-lint for compliance)

### Migration Order

1. **apache-https-website** (low risk, already in Ansible): Review and optimize the existing Ansible playbook
2. **ssl-poodle-fix** (low risk, already in Ansible): Review and optimize the existing Ansible playbook
3. **inspec-https-verification** (moderate complexity): Convert InSpec tests to Ansible assert modules or Molecule tests
4. **inspec-ssh-profile** (moderate complexity): Convert InSpec compliance tests to ansible-lint rules or OpenSCAP checks
5. **chef-automate-deployment** (high complexity): Create new Ansible playbooks to replace Chef Automate functionality

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The migration will maintain the same security posture and compliance requirements
3. Self-signed certificates are acceptable for the migrated solution (or will be replaced with proper CA-signed certificates)
4. The Chef Automate functionality is primarily used for compliance and infrastructure management, which can be replaced by Ansible Tower/AWX
5. No custom Chef cookbooks or recipes are in use beyond what's visible in the repository
6. The Test Kitchen testing workflow will be replaced with an equivalent Ansible-native testing approach
7. The hardcoded credentials in the deployment scripts will be properly secured in the migrated solution