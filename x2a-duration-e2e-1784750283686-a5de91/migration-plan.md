# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstration and testing purposes. The primary content consists of Ansible playbooks for configuring web servers with HTTPS support and SSL security fixes, along with Chef InSpec test files for compliance verification. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible content is already in place. The main focus will be on standardizing the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have performed a thorough search of the repository and can confirm:
- No Puppet modules found (searched for `**/manifests/init.pp` and `**/*.pp` - no matches)
- No Chef cookbooks found (searched for `**/recipes/default.rb` - no matches)
- No PowerShell modules found (searched for `**/*.psd1` - no matches)

The repository primarily contains Ansible playbooks and Chef InSpec tests rather than traditional Chef cookbooks or Puppet modules. The main components are:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH security compliance checks

- **chef_deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Convert to use Ansible's native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Static HTML file, can be directly used in Ansible content.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure setup if needed.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure setup if needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing within playbooks
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Consider integrating with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role/playbook testing

- **Apache2 (2.4.41-4ubuntu3.10)**: Continue using the same version in Ansible playbooks

- **OpenSSL (unspecified version)**: Continue using the Ansible `openssl_*` modules

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.
  - Migration approach: Use the same configuration parameters in the standardized Ansible roles.

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls.

- **Self-signed Certificates**: The playbooks generate self-signed certificates for HTTPS.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Map InSpec resources to equivalent Ansible modules or testing framework constructs.

- **Chef Automate Deployment**: If Chef Automate is still needed for other purposes, determine how to integrate with Ansible.
  - Mitigation strategy: Either maintain the shell scripts separately or create Ansible playbooks that can deploy Chef Automate when needed.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Standardize the playbook structure and convert to an Ansible role
2. **poodle_fix.yml** (low risk, already Ansible): Standardize the playbook structure and convert to an Ansible role
3. **InSpec Tests** (moderate complexity): Convert to Ansible-compatible testing framework
4. **Chef Deployment Scripts** (optional): Convert to Ansible playbooks if Chef infrastructure is still needed

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, based on the README content.
2. The Chef InSpec tests are used for compliance verification of infrastructure configured by Ansible.
3. The Chef Automate and Chef Server deployment scripts may not need migration if the purpose is to demonstrate Chef capabilities.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
6. The Apache configuration is for a simple "Hello World" website and doesn't have complex dependencies.
7. The primary goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment.