# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Technologies**: Ansible, Chef InSpec, Bash scripts

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Two options:
  1. Convert InSpec tests to Ansible assertions using assert module
  2. Keep InSpec tests and integrate them with Ansible using the `community.general.inspec` module

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source version of Ansible Tower)
  - Ansible Semaphore
  - Ansible Runner

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance security:
  - Ensure TLS 1.2+ is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Add option for Let's Encrypt certificates instead of self-signed

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement:
  - Incorporate SSH hardening into Ansible roles
  - Use ansible.posix.ssh_config module for SSH configuration

- **Vault/secrets management**:
  - Current implementation has hardcoded credentials in the Chef server setup scripts
  - Migrate to Ansible Vault for secure credential storage
  - Credentials detected:
    - User password in deploy-automate.sh and deploy-chef-server.sh (hardcoded)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions may require additional logic:
  - Solution: Use the `community.general.inspec` module to run existing InSpec tests from Ansible
  - Alternative: Convert tests to equivalent Ansible assertions using assert, uri, and command modules

- **Chef Server Replacement**: The Chef Server setup scripts need to be replaced with Ansible inventory management:
  - Solution: Use AWX/Tower for web UI and inventory management
  - Alternative: Use Ansible inventory plugins and Git for version control

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Convert to Ansible roles with proper directory structure
   - Implement variable files to replace hardcoded values
   - Add documentation

2. **Testing Framework**:
   - Replace Test Kitchen with Ansible Molecule
   - Either integrate existing InSpec tests or convert to Ansible assertions

3. **Chef Server Setup Scripts**:
   - Convert bash scripts to Ansible playbooks for infrastructure setup
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The InSpec tests are valuable and should be preserved in some form
3. The target environment will continue to be Ubuntu-based systems
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The migration should maintain the same level of security compliance testing
6. No complex state management or data bags are in use
7. The Chef Automate/Server setup is for demonstration purposes and not a critical production environment