# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with InSpec testing
3. InSpec compliance profiles for security testing

The migration complexity is relatively low as most of the Ansible components are already in place. The main focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks. The estimated timeline for this migration is 1-2 weeks, depending on the complexity of the Chef Automate replacement.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
  - Migration considerations: Already in Ansible format, may need refactoring to follow best practices
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
  - Migration considerations: Already in Ansible format, may need refactoring to follow best practices
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
  - Migration considerations: Update to use Ansible-native testing frameworks like Molecule
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
  - Migration considerations: Convert to Ansible testing framework or maintain InSpec for testing
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance
  - Migration considerations: Convert to Ansible testing framework or maintain InSpec for testing
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
  - Migration considerations: Replace with Ansible playbook for deploying alternative configuration management or compliance tools
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server
  - Migration considerations: Replace with Ansible playbook for deploying alternative configuration management tools

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate**: Replace with Ansible AWX/Tower or another compliance/automation platform
- **Chef Infra Server**: Replace with Ansible AWX/Tower or GitOps-based approach
- **InSpec**: Either maintain InSpec for compliance testing or replace with Ansible-native testing frameworks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols
  - Migration approach: Maintain this security practice in the Ansible playbooks, update to include TLS 1.3
  
- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Maintain this security check, convert to Ansible-native testing if desired
  
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - Migration approach: Replace hardcoded credentials with Ansible Vault or external secrets management

### Technical Challenges

- **Compliance Testing**: The repository uses InSpec for compliance testing
  - Mitigation strategy: Either maintain InSpec for compliance testing or migrate to Ansible-native testing frameworks
  
- **Chef Automate Replacement**: Finding an equivalent replacement for Chef Automate functionality
  - Mitigation strategy: Evaluate Ansible AWX/Tower or other compliance platforms

### Migration Order

1. Ansible playbooks (chef-and-ansible/*.yml) - low risk, already in Ansible format
2. InSpec tests (chef-and-ansible/tests/*.rb) - moderate complexity, decide whether to maintain or replace
3. Chef deployment scripts (setup-automate/*.sh) - high complexity, requires replacement solution

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, as indicated in the README.md
2. The Chef components (Automate and Infra Server) are used for compliance automation and could be replaced with Ansible AWX/Tower
3. The InSpec tests are valuable and should be maintained or converted to equivalent Ansible tests
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The hardcoded credentials in the setup scripts are for demonstration purposes only
6. The repository is used for educational/demonstration purposes rather than production deployments