# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing primarily on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

Given the limited scope and the fact that part of the codebase is already in Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example showing how to use Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Keep InSpec but integrate it with Ansible using the `inspec` Ansible module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise management
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. This needs to be preserved in the migration.
  - Migration approach: Use the same Ansible modules (`openssl_privatekey`, `openssl_csr`, `openssl_certificate`) in the new playbooks.

- **SSH Hardening**: The InSpec tests check for SSH security compliance.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls tested by InSpec.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and assertions.

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible.
  - Mitigation: Create Ansible roles for deploying alternative infrastructure management solutions.

### Migration Order

1. Convert existing Ansible playbooks to proper Ansible roles (website_https.yml, poodle_fix.yml)
2. Create Ansible testing framework to replace InSpec tests
3. Create Ansible playbooks to replace Chef Automate/Infra Server deployment scripts

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production use.
2. The Chef InSpec tests are used for compliance validation of infrastructure deployed by Ansible.
3. The Chef Automate/Infra Server deployment scripts are separate from the main functionality and could be replaced with Ansible Tower/AWX.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only.