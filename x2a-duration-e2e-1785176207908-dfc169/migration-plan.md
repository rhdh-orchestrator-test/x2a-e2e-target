# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity since most of the content is already in Ansible format.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG/CCI)

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL protocols and ciphers are maintained during migration.
  - Migration approach: Preserve the SSL protocol restrictions (disabling SSLv3, enabling TLSv1.2) in the Ansible roles.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or continue using InSpec for verification.

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be handled securely

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible verification methods.
  - Mitigation: Consider using Ansible assert modules or maintaining InSpec as a testing tool called from Ansible.

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with equivalent Ansible roles.
  - Mitigation: Create Ansible roles that perform the same system configuration and Chef server installation steps.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk since they're already in Ansible format, just need organization into proper roles and structure.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing methods.
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity to convert bash scripts to Ansible roles.

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The InSpec tests are intended to be run against systems configured by the Ansible playbooks.
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced entirely by Ansible.
4. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure credential management.
5. The Test Kitchen configuration is used for local testing and would be replaced with a CI/CD pipeline.