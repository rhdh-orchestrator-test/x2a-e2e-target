# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef InSpec test profiles for compliance validation
2. Ansible playbooks for configuration management
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is relatively low as most configuration is already in Ansible format. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

Estimated timeline: 2-3 weeks for a complete migration, with the majority of time spent on converting the InSpec tests and creating Ansible playbooks for Chef server deployment.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef_automate_deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **ssh_profile**:
    - Description: InSpec test profile for validating SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login validation, compliance with security standards

- **website_https_verify**:
    - Description: InSpec test profile for validating HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS response testing, SSL protocol validation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server
- `README.md`: Documentation files explaining the purpose of the repository

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Replace with Ansible Molecule
  - For compliance testing: Use ansible-lint with custom rules or integrate with OpenSCAP
  
- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Semaphore (lightweight alternative)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (already implemented in poodle_fix.yml)
  - Consider adding OCSP stapling and stronger cipher suites
  
- **SSH Hardening**: The InSpec tests validate SSH security configurations:
  - Create equivalent Ansible roles for SSH hardening
  - Implement ansible-lint rules to validate SSH configurations
  
- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Self-signed certificates generated in website_https.yml
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Molecule doesn't have direct equivalents for all InSpec resources
  - Consider using Molecule with Testinfra for Python-based testing
  - Alternative: Keep InSpec as a standalone testing tool even with Ansible

- **Chef Server Deployment**: Creating Ansible playbooks to replace the Chef server deployment scripts:
  - Need to research Ansible modules for Chef server API interaction
  - Consider if Chef server is still needed or if it can be replaced entirely with Ansible

### Migration Order

1. **website_https.yml and poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize existing Ansible code
   - Add documentation and improve variable naming

2. **InSpec Tests** (moderate complexity)
   - Convert ssh_profile.rb to Ansible Molecule tests
   - Convert website_https_verify.rb to Ansible Molecule tests
   - Alternatively, create an Ansible role that installs and runs InSpec tests

3. **Chef Server Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement Ansible Vault for credential storage
   - Consider if Chef server deployment is still needed or can be replaced with Ansible Automation Platform

### Assumptions

1. The primary goal is to move all configuration management to Ansible, not just convert Chef code to Ansible
2. The InSpec tests are still valuable and need to be preserved in some form
3. The Chef server deployment scripts are still needed (rather than being replaced entirely by Ansible Automation Platform)
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external Chef cookbooks or roles are being used that weren't discovered in the repository
6. The security requirements (SSH hardening, SSL configuration) will remain the same
7. No CI/CD pipeline integration was found, so no assumptions about CI/CD tools