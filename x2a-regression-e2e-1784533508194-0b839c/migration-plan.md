# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL and InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache deployment, SSL configuration, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with SSL. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality. Should be migrated to Ansible test framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible test framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Create an Ansible role that installs and configures equivalent monitoring and compliance tools
  
- **Chef Server CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Replace with Ansible AWX/Tower for centralized configuration management
  
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Ansible Molecule for integration testing
  - Option 3: Implement custom Ansible tasks to perform the same compliance checks

### Security Considerations

- **SSL Configuration**: The migration must maintain the secure SSL configuration (TLSv1.2) and disable vulnerable protocols (SSLv3)
  - Migration approach: Preserve the same SSL configuration parameters in the Ansible tasks
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Create Ansible tasks to enforce and verify the same SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password')
  - SSL certificates generated and managed in playbooks
  - Migration approach: Replace hardcoded credentials with Ansible Vault and implement proper certificate management
  - Count of credentials detected: 2 sets of credentials in setup-automate scripts

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible assert modules or custom modules to perform the same compliance checks
  - Example: Replace InSpec port check with Ansible's wait_for module
  
- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent infrastructure
  - Mitigation: If Chef Automate functionality is still needed, create Ansible roles to deploy alternative configuration management or compliance tools
  - Example: Deploy Prometheus/Grafana for monitoring and OpenSCAP for compliance

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to the new Ansible structure
   - Update any deprecated syntax or modules

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible-native testing solutions
   - Implement equivalent compliance checks using Ansible

3. **Chef Deployment Scripts** (Higher complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Replace Chef-specific functionality with Ansible equivalents

### Assumptions

1. The primary goal is to consolidate all infrastructure management to Ansible, eliminating the dependency on Chef
2. The InSpec compliance testing functionality needs to be preserved in some form
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible functionality
4. The target environment will remain Ubuntu-based systems
5. The hardcoded credentials in the deployment scripts are for testing purposes only and will be properly secured in the migrated solution
6. The Test Kitchen testing framework will be replaced with an Ansible-native testing solution
7. The Apache web server configuration and SSL settings need to be preserved in the migration
8. The repository is primarily used for demonstration purposes as indicated by the main README.md