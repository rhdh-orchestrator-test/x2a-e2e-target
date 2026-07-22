# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need to be migrated to a pure Ansible solution. The repository appears to be primarily educational in nature, demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with two Ansible playbooks, two Chef InSpec test files, and two Chef server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

**CRITICAL PATH VERIFICATION:**
All module paths have been verified to exist using the `list_directory` tool:
- chef-and-ansible/website_https.yml - Verified
- chef-and-ansible/poodle_fix.yml - Verified
- chef-and-ansible/tests/ssh_profile.rb - Verified
- chef-and-ansible/tests/website_https_verify.rb - Verified
- setup-automate/deploy-automate.sh - Verified
- setup-automate/deploy-chef-server.sh - Verified

No Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), or PowerShell modules (.psd1) were found in the repository.

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Static HTML content for the website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides native testing for Ansible roles and playbooks
  - Can use the same Vagrant driver for consistency

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Galaxy for role sharing
  - Git repositories for version control

### Security Considerations

- **SSL Configuration**: The current playbooks properly configure SSL with TLS 1.2 and disable vulnerable protocols. This should be maintained in the migrated solution.
  - Migration approach: Keep the same SSL configuration parameters in the Ansible tasks

- **SSH Security**: The InSpec test verifies SSH root login is disabled, which is a critical security control.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint rules to verify this configuration

- **Self-signed Certificates**: The current solution generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
  - Migration approach: Add optional Let's Encrypt support using Ansible's `acme_certificate` module

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test functionality.
  - Mitigation: Create a test mapping document and validate each test case individually

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely replaced with Ansible roles for infrastructure management.
  - Mitigation: Evaluate AWX/Tower deployment options or create custom Ansible roles for centralized management

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (Priority 1, already Ansible): No migration needed, already in Ansible format
2. **ssh_profile.rb** and **website_https_verify.rb** (Priority 2): Convert InSpec tests to Ansible assertions or Molecule tests
3. **deploy-automate.sh** and **deploy-chef-server.sh** (Priority 3): Replace with Ansible roles for infrastructure management

### Assumptions

1. The repository is primarily educational/demonstrative and not used in production environments
2. The InSpec tests are used for validation only and not part of a larger compliance framework
3. There are no external dependencies or integrations not visible in the repository
4. The Apache configuration is relatively simple and doesn't include complex customizations
5. The Chef server deployment scripts are standalone and not integrated with other systems
6. No specific version requirements exist for Ansible beyond what's needed to support the current functionality
7. No specific performance requirements exist that would impact the migration approach