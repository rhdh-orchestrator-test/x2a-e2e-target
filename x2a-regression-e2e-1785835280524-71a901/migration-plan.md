# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks and InSpec tests into a standardized Ansible structure
3. Preserving the compliance testing functionality currently provided by InSpec

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
  - Migration strategy: Convert InSpec tests to Ansible assert tasks or Molecule verifiers
  - Alternative: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
  - Migration strategy: Create equivalent Molecule scenarios for each existing Test Kitchen suite

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles
  - Migration strategy: Create Ansible roles that perform equivalent setup tasks

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and implement security hardening
  - Migration approach: Preserve the SSL configuration in the Ansible playbooks, ensuring TLSv1.2 is enforced
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions
  - Mitigation strategy: Use Ansible's assert module or consider keeping InSpec as a testing tool called from Ansible

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent functionality
  - Mitigation strategy: Determine if Chef Server is still needed or if it can be replaced entirely with Ansible

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format, just need restructuring
2. **InSpec Tests** (chef-and-ansible/tests/*.rb): Moderate complexity to convert to Ansible assertions
3. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity, requires creating equivalent Ansible roles

### Assumptions

1. The primary goal is to consolidate on Ansible and eliminate Chef dependencies
2. InSpec testing functionality needs to be preserved in some form
3. The Chef Automate/Server deployment is still required (rather than being eliminated)
4. The target environment will remain Ubuntu-based
5. No external inventory or complex multi-node orchestration is currently in use
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives