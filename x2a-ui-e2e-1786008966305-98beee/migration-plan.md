# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, and SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Verifies SSH root login is disabled according to security standards

- **automate-deploy**:
    - Description: Shell script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Configures hostname, system parameters, downloads and installs Chef Automate, creates user and organization

- **chef-server-deploy**:
    - Description: Shell script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Similar to automate-deploy but only installs Chef Infra Server

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML template used in the website_https playbook. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider OpenSCAP with ansible-lockdown or ansible-hardening roles

- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing infrastructure code
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - AWX/Ansible Tower for automation
  - Compliance solutions like OpenSCAP, Wazuh, or Tenable for compliance reporting

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve security by:
  - Using modern TLS configurations (TLS 1.2/1.3 only)
  - Implementing proper certificate management
  - Following current best practices for web server security

- **SSH Hardening**: The InSpec profile checks SSH security. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Implement equivalent checks using Ansible or another testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-native testing will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent checks using Ansible's assert module, Molecule, or other testing frameworks
  - Ensuring the same level of reporting and documentation

- **Deployment Scripts Conversion**: Converting the Chef Automate/Server deployment scripts to Ansible:
  - If Chef Automate/Server is still needed, create Ansible roles to deploy them
  - If not needed, identify alternative solutions for the functionality they provide

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to a proper Ansible role structure with variables
2. **poodle_fix.yml** (low risk, already Ansible): Incorporate into the Apache/web server role
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing solutions
4. **Deployment Scripts** (high complexity): Convert to Ansible roles or replace with alternative solutions

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. The InSpec tests are valuable and need to be preserved in some form
3. The deployment scripts for Chef Automate/Server may not be needed if Chef is being replaced
4. The current Ansible playbooks follow an older, less structured approach and would benefit from conversion to roles
5. No external inventory or variable files exist beyond what's in the repository
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. The security requirements expressed in the InSpec tests must be maintained
8. No complex data structures or external data sources are being used