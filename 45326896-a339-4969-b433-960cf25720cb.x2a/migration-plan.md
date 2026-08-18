# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring existing Ansible playbooks follow best practices
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Static HTML file used in the website deployment. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Continue using InSpec but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific test frameworks

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise features
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved during migration.
  - Migration approach: Directly port the SSL configuration to Ansible roles with proper variable management.

- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assert statements or Molecule tests.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, which is acceptable for testing but should use proper certificate management in production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require different approaches to validation.
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios.

- **Chef Server Deployment**: The Chef server deployment scripts contain specific Chef-related commands that need Ansible equivalents.
  - Mitigation: Create Ansible roles that install and configure AWX/Tower or other Ansible management platforms.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need to be converted to roles and follow best practices.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, need to be converted to Ansible-compatible testing frameworks.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, need to be completely rewritten as Ansible playbooks.

### Assumptions

1. The repository is primarily for demonstration purposes and not a production deployment.
2. The InSpec tests are used for validation after Ansible playbook execution.
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced with Ansible infrastructure.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. No external dependencies or integrations beyond what's visible in the repository.
6. The migration will maintain the same level of security validation currently provided by InSpec tests.