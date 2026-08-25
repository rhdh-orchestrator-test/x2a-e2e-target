# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The repository appears to be primarily a demonstration of how Chef InSpec can be used alongside Ansible for compliance testing, rather than a full production infrastructure codebase. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, focusing on:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Ensuring the existing Ansible playbooks follow best practices
3. Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and small number of files, this migration could be completed in approximately 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the website example

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other compliance tools like DISA STIG or CIS Benchmarks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure that:
  - Modern TLS protocols are enforced (already addressed in poodle_fix.yml)
  - Cipher suites are properly configured
  - Certificate management is handled securely

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require finding equivalent ways to test:
  - Port listening status
  - HTTP/HTTPS responses
  - SSL protocol configuration
  - Mitigation: Use Ansible's uri module and assert module to create equivalent tests

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible:
  - Challenge: Ensuring idempotence in the deployment process
  - Mitigation: Use Ansible's command module with creates/changed_when to ensure idempotence

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and update to follow Ansible best practices
   - Convert to a proper role structure

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and update to follow Ansible best practices
   - Consider merging with website_https as a single role

3. **website_https_verify.rb** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests

4. **Chef deployment scripts** (high complexity)
   - Convert bash scripts to Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The target environment will continue to be Ubuntu 20.04
3. Vagrant will continue to be used for development/testing
4. The Chef InSpec tests need to be converted to Ansible-native testing rather than maintained separately
5. The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible rather than maintained as bash scripts
6. No external dependencies or modules are required beyond what's already in the repository
7. The migration will maintain the same functionality but follow Ansible best practices