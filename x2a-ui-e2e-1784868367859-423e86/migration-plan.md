# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing files and Ansible playbooks that are used for compliance automation demonstrations. The repository appears to be a set of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Migrating Chef InSpec tests to Ansible-compatible testing frameworks
2. Ensuring existing Ansible playbooks follow best practices
3. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

Given the limited scope and example nature of the repository, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible technologies.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic examples that could run on-premises or in any cloud

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Automation Platform for a fully supported solution

### Security Considerations

- **SSL Configuration**: The `poodle_fix.yml` playbook addresses SSL security by enforcing TLSv1.2. This should be maintained in the migrated solution.
  
- **SSH Hardening**: The `ssh_profile.rb` InSpec test verifies SSH root login is disabled. This security check should be converted to an Ansible-compatible test.

- **Self-signed Certificates**: The `website_https.yml` playbook generates self-signed certificates. In production, consider using Let's Encrypt or another trusted CA.

- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (user login credentials)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use Ansible's `assert` module for simple checks and consider integrating with specialized testing tools for more complex scenarios.

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible will require understanding the Chef Server installation process.
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts, using Ansible modules instead of shell commands where possible.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. Focus on improving structure and following best practices.
   
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing.
   
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to convert to Ansible playbooks.

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment, based on the README content.
   
2. The InSpec tests are used for compliance validation rather than infrastructure testing.
   
3. The deployment scripts are examples and may need customization for actual production use.
   
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
   
5. The migration goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment.
   
6. No external data sources or complex state management is required based on the current repository content.
   
7. The security configurations in the examples (SSL, SSH) represent minimum requirements that should be maintained or enhanced in the migration.