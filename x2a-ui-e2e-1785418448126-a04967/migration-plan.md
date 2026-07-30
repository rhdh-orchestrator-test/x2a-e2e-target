# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration environment showing how Chef InSpec can be used alongside Ansible for compliance automation. It also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and their straightforward nature.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, and SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Verifies SSH root login is disabled, includes STIG references

### Infrastructure Files

- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for deploying alternative compliance tools.
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server only. Migration consideration: Replace with Ansible playbook for deploying alternative configuration management tools.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Use ansible-lint with custom rules
  - For infrastructure testing: Use Molecule with testinfra or Ansible's assert module
  - For continuous compliance: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL/TLS configurations
  
- **SSH Security**: The SSH compliance checks in ssh_profile.rb need to be preserved
  - Approach: Create an Ansible role for SSH hardening that implements the same controls
  - Create corresponding Ansible-based tests to verify compliance

- **Vault/secrets management**:
  - No explicit secrets management was detected in the repository
  - The deploy scripts contain hardcoded credentials that should be moved to Ansible Vault in the migration

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible assert modules or testinfra with Molecule for functional testing
  - For compliance testing, consider using ansible-lint with custom rules or integrating with OpenSCAP

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem
  - Mitigation: Consider AWX/Tower for orchestration and dashboard functionality
  - For compliance reporting, evaluate integration with tools like OpenSCAP or Compliance as Code frameworks

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and integrate into a comprehensive Apache security role
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing approaches
4. **Deployment Scripts** (high complexity): Create Ansible playbooks to replace the Chef Automate deployment scripts

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The InSpec tests are used for validation and compliance checking rather than as part of a larger compliance framework
3. There are no external dependencies or integrations not visible in the repository
4. The deployment scripts are used for setting up test environments rather than production systems
5. No custom Chef resources or complex logic is present that would require special handling during migration
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only