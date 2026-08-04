# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and demonstration purposes. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible playbooks

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing with Ansible-native testing frameworks.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements
  - Install and configure equivalent monitoring and compliance tools
  - Set up users and organizations in the new environment

### Security Considerations

- **SSL Configuration**: The existing playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Consider using Let's Encrypt instead of self-signed certificates
  - Implement proper certificate rotation

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this security check
  - Implement the actual SSH hardening in Ansible if not already present

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require different approaches:
  - Challenge: InSpec has rich testing capabilities specifically designed for compliance
  - Mitigation: Consider using a combination of Ansible assert, custom modules, and external tools like Molecule

- **Maintaining Compliance Automation**: The repository is focused on compliance automation:
  - Challenge: Ensuring the same level of compliance validation after migration
  - Mitigation: Document compliance requirements and ensure new Ansible roles satisfy them

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format; just need review and potential refactoring
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-compatible testing frameworks
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes as indicated by the README.md
2. The Chef InSpec tests are used alongside Ansible for compliance validation
3. There are no actual Chef cookbooks to migrate, only InSpec tests
4. The deployment scripts are used for setting up Chef infrastructure, which will be replaced with equivalent Ansible management tools
5. The target environment will continue to be Ubuntu 20.04 or similar
6. The security requirements (SSH configuration, SSL protocols) will remain the same
7. No external dependencies or integrations beyond what's visible in the repository