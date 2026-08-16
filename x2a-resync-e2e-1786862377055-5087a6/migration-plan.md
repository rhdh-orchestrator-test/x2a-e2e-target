# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests, Ansible playbooks, and Bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with most components already using Ansible. The primary migration effort will focus on converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as the repository is primarily focused on examples and demonstrations rather than production infrastructure.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a simple HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **compliance-tests**:
    - Description: Chef InSpec tests for verifying SSH configuration and HTTPS website
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS port and protocol verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file for website testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For SSH configuration tests: Use Ansible's `assert` module with `ansible.builtin.command` to check SSH configuration
  - For website HTTPS tests: Use Ansible's `uri` module to verify website functionality and `openssl_certificate_info` module to verify SSL/TLS protocols

- **Chef Automate CLI**: Replace with Ansible roles for:
  - Chef Automate deployment
  - Chef Infra Server deployment
  - User and organization management

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Maintain the same security posture using Ansible's `lineinfile` or `template` modules
  
- **SSH Security**: InSpec tests verify that SSH root login is disabled
  - Migration approach: Include SSH hardening in the Ansible playbooks using the `ansible.posix.sshd_config` module

- **Vault/secrets management**:
  - Hardcoded credentials in Bash scripts (username, password, email)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's `assert` module combined with command/shell modules to perform similar checks
  - Consider using Molecule for testing Ansible roles

- **Chef Automate Deployment**: Ensuring the Chef Automate deployment works correctly with Ansible
  - Mitigation: Create a dedicated Ansible role that follows the same steps as the Bash scripts
  - Use Ansible's `command` module to run Chef Automate CLI commands when necessary

### Migration Order

1. Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks (high value)
2. Convert InSpec tests to Ansible-native tests (moderate complexity)
3. Refactor existing Ansible playbooks to follow best practices (low risk)

### Assumptions

1. The repository is primarily for demonstration purposes and not production infrastructure
2. The Chef InSpec tests are used alongside Ansible playbooks as described in the README
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The hardcoded credentials in the Bash scripts are for demonstration purposes only
5. The Chef Automate and Chef Infra Server deployment is intended for on-premises or generic cloud VMs
6. The repository is focused on showing how Chef InSpec can be used with Ansible rather than being a full infrastructure codebase