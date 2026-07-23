# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and server configuration. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks
3. Migrating Chef Automate/Infra Server deployment scripts to Ansible

The complexity is low to moderate, with an estimated timeline of 1-2 weeks for complete migration. The repository appears to be primarily educational/example-based rather than a production infrastructure codebase.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

**IMPORTANT NOTE: No traditional Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), or PowerShell modules (.psd1) were found in this repository. The following inventory lists the components that do exist and require migration.**

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration and TLS protocols
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Use Molecule's Vagrant driver to maintain similar local testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Consider using ansible-navigator for local development

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should:
  - Maintain TLS 1.2+ requirement
  - Use Ansible's `openssl_*` modules consistently
  - Consider using Let's Encrypt integration instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Include equivalent checks in Ansible
  - Consider using ansible.posix.ssh_config module for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count: 2 credential sets identified (user login credentials in setup scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic
  - Mitigation: Use Ansible assert module with well-structured conditions
  - Consider maintaining some tests in a specialized testing tool if complex assertions are needed

- **Test Kitchen to Molecule**: Ensuring test environments remain consistent during migration
  - Mitigation: Create equivalent Molecule scenarios that match current Test Kitchen configurations

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and improve variable usage
   - Implement idempotency checks

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule verifiers
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity
   - Create Ansible playbooks to replace bash scripts
   - Implement Ansible Vault for credential storage
   - Add proper error handling and idempotency

### Assumptions

1. The repository is primarily for educational/demonstration purposes rather than production use
2. The existing Ansible playbooks are functional and follow best practices
3. There are no external dependencies beyond what's visible in the repository
4. The InSpec tests are used for verification only and not for remediation
5. The deployment scripts are used for initial setup only and not for ongoing management
6. No complex data structures or external data sources are being used
7. No integration with external systems beyond what's visible in the code
8. The target environment is Ubuntu 20.04 as specified in kitchen.yml