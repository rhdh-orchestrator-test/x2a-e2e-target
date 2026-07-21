# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks, Chef InSpec tests, and Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on:

1. Maintaining the existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Replacing Chef Automate/Chef Server deployment scripts with Ansible playbooks

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary challenge will be converting the InSpec tests to an Ansible-compatible testing framework while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configurations, specifically checking that root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH security compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `chef-and-ansible/index.html`: Sample HTML file used for testing the web server configuration.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml and targeted by the Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks that perform equivalent server setup
  - Consider using the official Chef collection for Ansible if Chef infrastructure is still required

### Security Considerations

- **SSL/TLS Configuration**: The `poodle_fix.yml` playbook addresses SSL/TLS security. Ensure this security hardening is maintained in the migrated solution.
  - Migration approach: Keep the existing Ansible playbook as is, but consider updating it to include more recent TLS security best practices.

- **SSH Security**: The `ssh_profile.rb` InSpec test verifies SSH security configurations.
  - Migration approach: Convert the InSpec test to Ansible assertions or Molecule tests that verify the same SSH security controls.

- **Self-signed Certificates**: The `website_https.yml` playbook generates self-signed certificates.
  - Migration approach: Keep the existing Ansible certificate generation but consider enhancing it with more secure key sizes and modern algorithms.

- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Consider using Molecule which provides a more structured testing framework for Ansible.

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible requires understanding of Chef Server's installation and configuration process.
  - Mitigation: Create a detailed Ansible role that replicates the Chef Server setup process, or use the official Chef collection for Ansible.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and update as needed
   - Update to use Ansible Vault for any sensitive data

2. **Testing Framework** (InSpec tests): Moderate complexity
   - Set up Molecule or alternative testing framework
   - Convert InSpec tests to the chosen framework
   - Ensure all compliance checks are maintained

3. **Chef Server Deployment**: High complexity
   - Create Ansible playbooks to replace the bash scripts
   - Implement secure credential management with Ansible Vault
   - Test deployment thoroughly

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool while maintaining the same functionality and security controls.
2. The InSpec tests are used primarily for validation and can be replaced with equivalent Ansible-compatible testing.
3. Chef Automate and Chef Server deployment scripts are used for setting up test environments and can be replaced with equivalent Ansible playbooks.
4. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes.
5. Test Kitchen is used only for testing and can be replaced with an Ansible-native testing framework.
6. No actual Chef cookbooks or recipes are being used for configuration management in this repository.