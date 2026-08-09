# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

**Timeline Estimate**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
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
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for validating HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test for validating SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate if still needed, or migrate to alternative solutions like AWX/Ansible Tower
- **Chef InSpec**: Maintain InSpec tests as they are compatible with Ansible, or convert to Ansible's built-in testing capabilities
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL Configuration**: Maintain the security hardening in the poodle_fix.yml playbook
- **SSH Hardening**: Preserve the SSH security controls validated by the InSpec tests
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture and configuration
  - Mitigation: Create dedicated Ansible roles for Chef Automate deployment or consider migrating to Ansible Tower/AWX
  
- **InSpec Test Integration**: Ensuring InSpec tests continue to work with the migrated Ansible playbooks
  - Mitigation: Maintain the existing InSpec tests and update the test execution framework (from Test Kitchen to Molecule)

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need refactoring to follow best practices
2. **Chef Automate Deployment Scripts**: Moderate complexity, requires converting bash scripts to Ansible playbooks
3. **Testing Framework**: Replace Test Kitchen with Ansible Molecule while preserving InSpec tests

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README indicating it's for "examples" and "how-tos"
2. The Chef Automate deployment is still required in the migrated solution (rather than being replaced entirely)
3. InSpec tests should be preserved for compliance validation rather than being replaced with Ansible-native testing
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions