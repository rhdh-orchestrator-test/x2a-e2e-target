# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure and replacing Chef InSpec tests with Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity for the Ansible playbooks and moderate complexity for replacing the InSpec testing framework.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Unknown (file exists but content not examined)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Static HTML file, purpose unknown. Migration consideration: Include as-is in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **kitchen-ansible**: Replace with Ansible Molecule for testing
- **kitchen-inspec**: Replace with Ansible Molecule with testinfra or ansible-lint
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with testinfra for functional testing
  - Option 2: ansible-test for integration testing
  - Option 3: ansible-lint for static analysis

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Migration approach: Convert to Ansible role with proper variable parameterization
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Use Ansible's crypto modules (openssl_*) with proper variable parameterization

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing frameworks
  - Mitigation strategy: Use Molecule with testinfra to achieve similar functionality
  
- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible
  - Mitigation strategy: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower

### Migration Order

1. **website_https.yml** (Priority 1, low risk): Convert to Ansible role with proper variable parameterization
2. **poodle_fix.yml** (Priority 1, low risk): Convert to Ansible role or include in the website_https role
3. **InSpec Tests** (Priority 2, moderate complexity): Convert to Molecule with testinfra
4. **Chef Deployment Scripts** (Priority 3, high complexity): Convert to Ansible roles or replace with AWX/Tower

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README.md content
2. The Chef InSpec tests are used for compliance validation of Ansible-managed infrastructure
3. The Chef Automate and Chef Infra Server deployment scripts may be legacy components that could be replaced with Ansible AWX/Tower
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or complex module relationships exist beyond what's visible in the repository
6. The migration will standardize on Ansible-native solutions rather than maintaining a hybrid Chef/Ansible approach