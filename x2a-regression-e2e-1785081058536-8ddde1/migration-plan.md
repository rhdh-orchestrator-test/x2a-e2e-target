# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a standardized Ansible structure
3. Preserving the Chef InSpec testing capabilities within an Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with SSL/TLS for a "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
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
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: Chef InSpec test file (content not examined)

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly defined in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but deployment scripts are designed for both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a testing framework, integrate with Ansible using the `ansible.builtin.shell` module to run InSpec tests or migrate to Ansible's built-in `assert` module where appropriate
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that perform equivalent setup

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (as in poodle_fix.yml)
  - Migrate self-signed certificate generation to Ansible's `openssl_*` modules (already using Ansible modules)

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Identified credentials: username, password, email in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef InSpec Testing**: Preserving the compliance testing capabilities of InSpec while moving to an Ansible-only workflow
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests as part of Ansible playbooks
  
- **Chef Server Deployment**: Replacing Chef Automate/Infra Server with equivalent functionality
  - Mitigation: Determine if Chef Server is still needed or if Ansible can fully replace its functionality

### Migration Order

1. **Ansible Playbooks Structure** (Low risk, foundation for other work)
   - Reorganize existing Ansible playbooks into proper roles and structure
   - Create variables files to replace hardcoded values

2. **Chef Deployment Scripts** (Moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Move credentials to Ansible Vault

3. **Testing Framework** (Higher complexity)
   - Set up Molecule for Ansible testing
   - Integrate InSpec tests with Ansible or convert to equivalent Ansible assertions

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The Chef InSpec tests are valuable and should be preserved in some form
3. The end goal is to have a fully Ansible-managed infrastructure without Chef components
4. The Apache configuration and SSL setup requirements will remain the same
5. The Chef Automate/Infra Server deployment may be replaced entirely by Ansible functionality
6. No external systems or services depend on the current Chef implementation