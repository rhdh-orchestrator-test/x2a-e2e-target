# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Existing Ansible playbooks that use Chef InSpec for compliance testing
2. Bash scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary work involves:
- Preserving the existing Ansible playbooks
- Converting the Chef InSpec tests to Ansible-native testing solutions
- Converting the Chef Automate/Infra Server deployment scripts to Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but call it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Or continue using Test Kitchen with the Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security properly by:
  - Generating proper SSL certificates
  - Disabling vulnerable SSL protocols (SSLv3)
  - Enabling secure protocols (TLSv1.2)
  - This should be preserved in the migrated solution

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Disabling root login
  - This should be implemented in the migrated Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts:
    - Username, password, and email in deploy-automate.sh and deploy-chef-server.sh
    - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing may require:
  - Learning Ansible's testing capabilities
  - Implementing custom modules or scripts for complex tests
  - Mitigation: Use Ansible's built-in modules like `uri`, `command`, and `assert` for testing

- **Chef Automate/Infra Server Deployment**: Converting the deployment scripts to Ansible:
  - Understanding the Chef Automate deployment process
  - Ensuring idempotence in the Ansible playbooks
  - Mitigation: Use Ansible's package management and command modules with proper conditionals

### Migration Order

1. **Existing Ansible Playbooks** (low risk, already in Ansible):
   - Preserve website_https.yml and poodle_fix.yml as they are already in Ansible format
   - Update any deprecated syntax or modules to current Ansible best practices

2. **InSpec Tests** (moderate complexity):
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible assertions or keep as InSpec and call from Ansible

3. **Chef Deployment Scripts** (high complexity):
   - Convert deploy-automate.sh to an Ansible playbook
   - Convert deploy-chef-server.sh to an Ansible playbook
   - Implement proper secret management for credentials

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the main README.md
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up Chef infrastructure
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no complex Chef cookbooks or recipes that need migration, only deployment scripts
6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already following Ansible best practices
7. No external dependencies or third-party Ansible roles are being used
8. The migration will preserve the functionality of the existing code while moving everything to Ansible
9. The hardcoded credentials in the deployment scripts are for demonstration purposes only