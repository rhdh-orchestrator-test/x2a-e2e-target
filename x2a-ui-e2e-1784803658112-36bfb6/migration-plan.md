# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible playbooks

Given the limited scope and small number of files, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS response testing, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server. No migration needed, can be used as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Server**: Replace with Ansible AWX/Tower or other Ansible-compatible automation platforms

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Testing Framework Conversion**: Converting Chef InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for simple tests, or integrate with Molecule for more comprehensive testing.

- **Chef Server Deployment**: Converting Chef Server deployment scripts to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef Server deployment or consider replacing Chef Server entirely with Ansible AWX/Tower.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Consolidate into a single role if appropriate

2. **InSpec Tests** (moderate complexity)
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests

3. **Chef Server Deployment Scripts** (high complexity)
   - Convert deploy-automate.sh and deploy-chef-server.sh to Ansible playbooks
   - Implement proper secret management using Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes showing how Chef InSpec can work alongside Ansible, rather than a production infrastructure repository.
2. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
3. The current setup uses Vagrant for local testing, which will likely continue to be used.
4. There are no external dependencies or integrations beyond what's visible in the repository.
5. The Chef Automate and Chef Server deployment scripts are intended for on-premises or generic cloud VM deployments.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
7. The migration will maintain the same functionality but consolidate everything into Ansible.