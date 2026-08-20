# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains a limited number of scripts and playbooks with clear functionality

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain or migrate to Ansible Molecule for testing
- **InSpec**: Maintain as a compliance testing tool, as it works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Maintain this security check
- **Credentials Management**: 
  - Current scripts have hardcoded credentials in bash scripts (username, password)
  - Migration should use Ansible Vault for secure credential storage
  - Count: 2 credential sets (one in each bash script)

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture
  - Mitigation: Create dedicated Ansible roles for Chef Automate and Chef Server deployment
  
- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation: Use Ansible's built-in support for InSpec or integrate with CI/CD pipeline

- **Testing Framework**: Migrating from Test Kitchen to Ansible-native testing
  - Mitigation: Consider using Molecule for testing Ansible roles and playbooks

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format
   - Review and refactor according to best practices
   - Organize into proper roles and playbooks structure

2. **Chef Deployment Scripts** (setup-automate/*.sh): Medium complexity
   - Convert bash scripts to Ansible roles
   - Implement secure credential management with Ansible Vault
   - Create idempotent deployment playbooks

3. **Testing Framework** (kitchen.yml and tests/*): Medium complexity
   - Decide on testing strategy (keep Test Kitchen or migrate to Molecule)
   - Ensure InSpec tests continue to work with new Ansible structure

### Assumptions

1. The repository is a demonstration/example repository rather than production code (based on README.md)
2. InSpec is being used alongside Ansible for compliance testing and should be maintained
3. The Chef Automate and Chef Server deployment scripts are intended for setting up Chef infrastructure, not for managing application configurations
4. The hardcoded credentials in the deployment scripts are examples and not production credentials
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. The Apache configuration is for demonstration purposes and may need enhancement for production use