# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **2-3 weeks**. The main effort will involve converting InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with HTTPS, SSL certificates, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed SSL certificates, Apache virtual host configuration, website deployment

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for Apache

- **website-https-compliance**:
    - Description: InSpec tests to verify HTTPS website configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-compliance**:
    - Description: InSpec tests to verify SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-server-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts with Chef server commands
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-compatible testing framework
- `index.html`: Sample HTML file for website testing - can be reused in Ansible playbooks
- `README.md`: Documentation files - will need updating to reflect new Ansible-only approach

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test for playbook validation
  - Option 3: ansible-lint for static analysis
  - Option 4: Keep InSpec but run it from Ansible using the command module

- **Test Kitchen (latest)**: Replace with:
  - Molecule for Ansible role testing
  - Or use ansible-test for playbook validation

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - CI/CD pipeline integration for automated testing

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with TLSv1.2 only, which should be maintained or updated to include TLSv1.3 in the Ansible migration
- **Self-signed Certificates**: The current solution uses self-signed certificates; consider integrating with Let's Encrypt for production environments
- **SSH Security**: The InSpec tests verify SSH root login is disabled; ensure this check is maintained in the Ansible migration
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec to Ansible test assertions and validate each test case individually
  
- **Chef Server Deployment**: Replacing Chef server deployment with Ansible automation
  - Mitigation: Create Ansible roles for AWX/Tower deployment that provide similar functionality to Chef Automate

- **Compliance Validation**: Ensuring the same level of compliance validation in the new Ansible framework
  - Mitigation: Consider using OpenSCAP with Ansible for compliance scanning or maintain InSpec as a separate tool called from Ansible

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible format)
2. **InSpec tests** conversion to Ansible-compatible testing (moderate complexity)
3. **Chef server deployment** scripts to Ansible playbooks (higher complexity)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. The migration is focused on moving to pure Ansible without maintaining Chef components
3. The current InSpec tests represent the complete compliance requirements
4. No external data sources or databases are involved in the current configuration
5. The Apache configuration does not have complex dependencies not visible in the provided files
6. The self-signed certificates approach is acceptable or will be replaced with proper certificate management
7. The current setup is for demonstration/testing purposes rather than production use
8. The hardcoded credentials in the deployment scripts are not used in production environments