# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing files and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be a set of examples rather than a full production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Chef InSpec test files that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible automation
3. Existing Ansible playbooks that need to be reviewed and potentially updated to current best practices

Given the limited scope and example nature of the repository, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance tagging (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use pure Ansible testing approach.
- `index.html`: Simple HTML file used for testing web server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider using OpenSCAP with Ansible or Ansible Compliance as Code modules

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set up equivalent monitoring and compliance scanning using Ansible Tower/AWX
  - Or deploy alternative compliance solutions like OpenSCAP

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Ensure the Ansible roles used for Apache configuration enforce TLSv1.2+ and disable older protocols

- **SSH Hardening**: The SSH compliance checks need to be maintained
  - Approach: Create Ansible roles that enforce the same SSH security controls and use Ansible-compatible testing to verify

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec, or consider using the ansible-lint tool with custom rules

- **Compliance Tagging**: The InSpec tests include compliance metadata (STIG, CCI references)
  - Mitigation: Ensure compliance metadata is preserved in the Ansible testing framework or documentation

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential updates to current best practices
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, need to be converted to Ansible playbooks
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Higher complexity, need to be converted to Ansible-compatible testing frameworks

### Assumptions

1. The repository is primarily for demonstration/example purposes and not a production codebase
2. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
3. Vagrant will continue to be used for local development/testing
4. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests need to be maintained
5. No external data sources or complex integrations are present beyond what's visible in the repository
6. The Chef Automate and Chef Infra Server deployment is a standalone example and not part of a larger Chef ecosystem
7. The migration is primarily focused on moving away from Chef tooling while maintaining the same functionality