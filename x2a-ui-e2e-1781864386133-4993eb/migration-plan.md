# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving:

1. Chef InSpec test profiles that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity. The primary focus will be on preserving the compliance testing capabilities while eliminating the Chef dependencies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, port checking, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Simple HTML file used for testing web server functionality - can be preserved as-is or incorporated into Ansible content

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, though the deployment scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for testing
  - Option 2: Use community.general.assert module for basic compliance checks
  - Option 3: Integrate with ansible-lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The existing playbooks already implement security best practices for SSL/TLS. Ensure these are preserved in the migrated solution:
  - Disabling SSLv3 (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - Proper certificate generation and management

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled. Ensure this security check is preserved in the Ansible-based solution.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (username/password in both deployment scripts)

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of InSpec resources to equivalent Ansible modules or testinfra methods.
  - Mitigation: Create a mapping document for InSpec resources to Ansible/testinfra equivalents

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs to be replicated in the Ansible solution.
  - Mitigation: Investigate AWX/Tower compliance reporting capabilities or integrate with a third-party compliance tool

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor refactoring for best practices
2. **InSpec Test Profiles** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires complete replacement with Ansible roles/playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 LTS
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (STIG references in ssh_profile.rb) need to be preserved
5. The deployment scripts are examples and not used in production (contain hardcoded credentials)
6. No external Chef cookbooks or complex Chef-specific features are in use that would complicate migration