# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts, Ansible playbooks with Chef InSpec testing, and InSpec profiles. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains a mix of Bash scripts, Ansible playbooks, and InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with SSL/TLS for a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

- **website_https_verify**:
    - Description: InSpec profile for verifying HTTPS configuration and SSL/TLS security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL/TLS protocol validation

- **ssh_profile**:
    - Description: InSpec profile for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

**CRITICAL PATH VERIFICATION:**
All module paths have been verified to exist using the `list_directory` or `file_search` tools:
- chef-and-ansible/website_https.yml - Verified
- chef-and-ansible/poodle_fix.yml - Verified
- setup-automate/deploy-automate.sh - Verified
- setup-automate/deploy-chef-server.sh - Verified
- chef-and-ansible/tests/website_https_verify.rb - Verified
- chef-and-ansible/tests/ssh_profile.rb - Verified

No Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), or PowerShell modules (.psd1) were found in the repository.

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used for testing the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible's built-in assert module where appropriate
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that accomplish the same server setup

### Security Considerations

- **SSL/TLS Configuration**: The playbooks enforce TLSv1.2 and disable older protocols. This security hardening should be maintained in the migrated Ansible playbooks.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **SSH Security**: The InSpec profile checks for SSH root login restrictions, which should be maintained in the Ansible configuration.
- **STIG Compliance**: The SSH profile includes STIG (Security Technical Implementation Guide) references that should be preserved in the Ansible implementation.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible-only deployments
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests as part of Ansible playbooks
  
- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible alternatives
  - Mitigation: Evaluate if Chef Server is actually needed or if Ansible can handle all configuration management needs

- **Compliance Testing**: Maintaining compliance validation capabilities
  - Mitigation: Either keep InSpec for testing or migrate to Ansible's native compliance capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Refactor to use Ansible roles for better organization
   - Update to use Ansible Vault for secrets
   - Integrate with Molecule for testing

2. **InSpec Profiles** (website_https_verify.rb, ssh_profile.rb): Medium complexity
   - Maintain as-is for testing or convert to Ansible assert modules
   - Integrate with Ansible workflow

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Convert to Ansible playbooks
   - Use Ansible Vault for credentials
   - Consider if Chef Automate/Server is still needed or can be replaced with Ansible Tower/AWX

4. **Testing Framework**: Medium complexity
   - Migrate from Test Kitchen to Molecule
   - Maintain InSpec tests but integrate with Ansible workflow

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The Chef Automate and Chef Infra Server deployment scripts are intended for educational/demonstration purposes, as they contain hardcoded credentials and simplified setup steps.

3. The primary value in this repository is the integration of InSpec testing with Ansible deployments, which should be preserved in the migration.

4. The target audience is likely users who are transitioning from Chef to Ansible or using both tools together, based on the white paper mentioned in the chef-and-ansible README.md.

5. The Apache configuration in the Ansible playbooks is a simplified example and may need enhancement for production use.

6. The InSpec profiles are intended to demonstrate compliance testing capabilities rather than provide comprehensive security validation.