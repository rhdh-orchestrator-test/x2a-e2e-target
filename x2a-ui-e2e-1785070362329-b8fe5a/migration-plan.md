# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstration and example purposes. The primary content consists of:

1. Ansible playbooks for configuring a web server with HTTPS
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with most components already in Ansible format. The primary migration effort will involve converting the Chef InSpec tests to Ansible-compatible testing frameworks and adapting the Chef server deployment scripts to Ansible playbooks. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for validating SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for Python-based testing
  - Option 2: ansible-test for built-in Ansible testing capabilities
  - Option 3: Continue using InSpec but invoke it directly rather than through Chef

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role and playbook testing
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks that configure equivalent monitoring and compliance solutions
  - Consider migrating to AWX/Ansible Tower for web UI and control capabilities

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks already implement TLS 1.2 and disable insecure protocols. This security practice should be maintained in the migrated solution.
  - Migration approach: Preserve the same configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained.
  - Migration approach: Create equivalent Ansible tasks to enforce this configuration and verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to an Ansible-compatible testing framework will require careful mapping of test assertions.
  - Mitigation: Create a mapping document between InSpec resources and their Ansible testing equivalents

- **Chef Server Functionality**: If the Chef Server is being used for actual configuration management, replacing its functionality will require more extensive planning.
  - Mitigation: Evaluate which Chef Server features are actually being used and map them to Ansible equivalents (AWX/Tower, GitLab CI, etc.)

### Migration Order

1. **website-https playbook** (already in Ansible format, low risk)
   - Review and optimize for Ansible best practices
   - Update testing framework

2. **poodle-fix playbook** (already in Ansible format, low risk)
   - Review and optimize for Ansible best practices
   - Update testing framework

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure all security checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes and not actively managing production infrastructure
2. The Chef InSpec tests are used for validation but not as part of a larger compliance framework
3. The Chef Automate and Chef Server deployment scripts are examples and not critical infrastructure components
4. No external Chef cookbooks or complex Chef-specific features are being used
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The migration will maintain the same level of security hardening present in the original configurations
7. No complex data transformation or state management is required during the migration