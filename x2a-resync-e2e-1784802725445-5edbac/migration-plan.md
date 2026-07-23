# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains a limited number of scripts and playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test for validating SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen with Ansible**: Maintain or migrate to Molecule for Ansible role testing
- **InSpec**: Maintain InSpec for compliance testing or consider migrating to Ansible's built-in assert module or other testing frameworks

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests validate SSH security configurations
  - Migration approach: Create Ansible tasks to implement the same SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform equivalent setup steps for a configuration management system
  
- **InSpec Integration**: Maintaining the InSpec tests with Ansible
  - Mitigation: Use Ansible's `shell` or `command` modules to run InSpec tests, or consider migrating to Ansible's built-in testing capabilities

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing Ansible code
   - Update to use Ansible best practices (roles, variables, etc.)

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Medium complexity
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

3. **Testing Framework** - Low complexity
   - Maintain InSpec tests or migrate to Ansible-native testing
   - Update Test Kitchen configuration or migrate to Molecule

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md
2. The Chef Automate and Chef Infra Server deployment scripts are intended for on-premises or cloud VM deployment
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The InSpec tests are intended to validate the Ansible playbook configurations
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
6. The repository is meant to showcase how Chef InSpec can be used alongside Ansible for compliance automation