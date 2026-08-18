# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining the InSpec testing framework for compliance validation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains deployment scripts and simple Ansible playbooks

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with InSpec tests for deploying and validating a secure Apache web server
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts with Chef commands
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration against POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance security:
  - Self-signed certificates are generated in the playbook
  - TLS 1.2 is enforced, disabling older protocols
  - Migration should maintain these security practices

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration should maintain this security practice
  - Consider expanding SSH hardening in the Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires:
  - Creating Ansible roles for Chef Automate installation
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  - Determining if Chef Automate is still needed or if it can be replaced entirely by Ansible

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible:
  - Ensure Ansible roles can be tested with InSpec
  - Consider using Ansible's built-in assert module for some tests
  - Maintain compliance validation capabilities

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Standardize existing Ansible playbooks
   - Update to follow best practices (roles, variables, etc.)

2. **Chef Automate/Infra Server Scripts** (Medium complexity)
   - Convert bash scripts to Ansible playbooks
   - Create roles for Chef server deployment if still needed
   - Implement Ansible Vault for credentials

3. **Testing Framework** (Low complexity)
   - Maintain InSpec tests
   - Consider adding Molecule for Ansible role testing

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. Chef Automate/Infra Server may still be needed after migration (if not, these components can be eliminated)
3. InSpec testing should be maintained for compliance validation
4. The existing Ansible playbooks are functional and follow reasonable practices
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or state management is required
7. The target environment is Ubuntu 20.04 on Vagrant VMs
8. No CI/CD pipeline integration is currently implemented