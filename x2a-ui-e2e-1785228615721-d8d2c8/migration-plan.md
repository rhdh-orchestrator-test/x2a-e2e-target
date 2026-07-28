# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure and migrating Chef InSpec tests to Ansible's native testing capabilities. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

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
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Static HTML file used in the website deployment. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible assert module
  - For more complex compliance testing: Use ansible-lint or migrate to Ansible's built-in test modules
  - Alternative: Keep InSpec tests but run them from Ansible using the command module

- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing infrastructure
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Can continue to use Vagrant as the driver for Molecule

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks
  - Create roles for system preparation
  - Create roles for package installation and configuration
  - Use Ansible Vault for credential management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration
  - Migration approach: Use Ansible's crypto modules (openssl_*) which are already being used
  - Ensure proper certificate management in the migrated solution

- **SSH Hardening**: InSpec tests verify SSH security configurations
  - Migration approach: Create Ansible role for SSH hardening that implements the same controls
  - Add Ansible assert statements to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities
  - Mitigation: Use Ansible's assert module for basic tests, consider keeping InSpec for complex compliance testing if needed
  - Alternative: Consider using ansible-test or molecule verify for more complex testing scenarios

- **Maintaining Compliance Standards**: The InSpec tests reference specific compliance standards (SRG-OS-000112, V-38607, etc.)
  - Mitigation: Document compliance mappings and ensure Ansible roles implement the same controls
  - Consider using ansible-lockdown roles which are mapped to security benchmarks

### Migration Order

1. **website_https.yml** (Priority 1, low risk): Convert to Ansible role with proper structure
2. **poodle_fix.yml** (Priority 1, low risk): Convert to Ansible role or include in the website_https role
3. **InSpec Tests** (Priority 2, moderate complexity): Convert to Ansible testing framework
4. **Chef Deployment Scripts** (Priority 3, moderate complexity): Convert to Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef InSpec tests are used for compliance validation of infrastructure configured by Ansible, showing an integration pattern between the two tools.
3. The setup-automate scripts are used for setting up a Chef environment, which may be used for testing or demonstration purposes.
4. The hardcoded credentials in the setup scripts are not used in production environments.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
6. The migration will maintain the same functionality but standardize on Ansible as the single automation tool.