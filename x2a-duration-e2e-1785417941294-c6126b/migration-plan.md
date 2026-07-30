# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests as a compliance verification layer

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache, SSL certificates, and proper configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain or migrate to Molecule for Ansible role testing
- **InSpec**: Maintain as compliance testing framework, integrate with Ansible workflow

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening for Apache (POODLE vulnerability fix)
  - Migration approach: Maintain the same configuration in Ansible, ensure idempotency
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible role to enforce SSH hardening based on InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles that perform the same system configuration and Chef Automate installation steps
  
- **InSpec Integration**: Maintaining InSpec tests with Ansible
  - Mitigation: Use Ansible's built-in integration with InSpec or create a custom integration

- **Test Kitchen**: Replacing Test Kitchen with Ansible-native testing tools
  - Mitigation: Migrate to Molecule for Ansible role testing while maintaining InSpec for compliance verification

### Migration Order

1. **chef-automate-deployment** (Medium complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Replace hardcoded credentials with Ansible Vault
   - Implement idempotency checks

2. **website-https-deployment** (Low complexity - already in Ansible)
   - Review and optimize existing Ansible playbook
   - Ensure best practices are followed
   - Maintain InSpec tests

3. **poodle-vulnerability-fix** (Low complexity - already in Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https-deployment as a role
   - Maintain InSpec tests

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md
2. The Chef Automate and Chef Infra Server deployment scripts are used for actual deployments
3. The InSpec tests are intended to be maintained as part of the compliance automation strategy
4. The hardcoded credentials in the deployment scripts are not used in production environments
5. The Ansible playbooks are already following best practices and only need minor adjustments
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. The migration will maintain the same functionality while improving security and maintainability