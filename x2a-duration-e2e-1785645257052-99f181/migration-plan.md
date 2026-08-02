# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

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
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `README.md`: Repository documentation

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Maintain but update configuration to use pure Ansible
- **InSpec**: Maintain as a compliance testing tool, which works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests verify SSH security configurations. Maintain these tests
- **Credentials in Scripts**: 
  - The deployment scripts contain hardcoded credentials (username, password)
  - Migration should use Ansible Vault for secure credential storage
  - Count: 2 credential sets (one in each deployment script)

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires:
  - Creating Ansible roles for Chef Automate installation
  - Managing system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  - Handling user and organization creation
  - Solution: Create dedicated Ansible roles for Chef infrastructure management

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible:
  - Solution: Use Ansible's built-in integration with InSpec or maintain separate InSpec test execution

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and optimize website_https.yml and poodle_fix.yml
   - Update to follow Ansible best practices (roles, variables, etc.)

2. **Chef Deployment Scripts** (Medium complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential management
   - Test deployment on target environments

3. **Test Kitchen Configuration** (Low complexity)
   - Update kitchen.yml to work with pure Ansible
   - Ensure InSpec tests continue to function

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. InSpec will continue to be used for compliance testing alongside Ansible
3. The Chef Automate and Chef Server deployment scripts are intended to be converted to Ansible rather than maintained as-is
4. The target environment will continue to be Ubuntu 20.04 or similar
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or state management requirements
7. No specific performance requirements for the migrated solution