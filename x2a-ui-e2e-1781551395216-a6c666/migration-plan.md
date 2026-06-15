# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-native testing solutions
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles and playbooks
  - Option 2: Ansible Assert module for basic validation within playbooks
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with:
  - Ansible Molecule for a complete testing workflow
  - Or continue using Test Kitchen with Ansible verifier instead of InSpec

- **Chef Automate/Chef Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements
  - Deploy alternative compliance and infrastructure management solutions

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement
  - Ensure proper certificate handling

- **SSH Security**: Preserve the SSH hardening checks from the InSpec profile
  - Convert the root login restriction check to Ansible assert or Molecule verification

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Recommend using Ansible Vault for securing these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to replicate InSpec tests
  - Alternative: Implement Molecule scenarios that perform equivalent validations

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with tools like AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The hardcoded credentials in the setup scripts are for demonstration purposes only
5. The migration aims to eliminate Chef components while preserving or enhancing the security validation capabilities
6. No specific compliance framework requirements beyond the STIG references in the SSH profile