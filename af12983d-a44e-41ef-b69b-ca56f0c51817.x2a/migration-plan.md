# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks used for demonstrating compliance automation. The migration will focus on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, the Chef server deployment scripts need to be converted to Ansible playbooks.

**Scope**: Small to medium complexity
**Timeline Estimate**: 1-2 weeks
**Primary Technologies**: Chef InSpec, Ansible Playbooks, Bash deployment scripts

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment and testing, SSL/TLS compliance verification, Apache configuration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user and organization creation, system configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec verification
  - Migration: Convert to Ansible Molecule for testing
  
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website
  - Migration: Keep as-is, already in Ansible format
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
  - Migration: Keep as-is, already in Ansible format
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification
  - Migration: Convert to Ansible assert tasks or Ansible Molecule verify
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
  - Migration: Convert to Ansible assert tasks or Ansible Molecule verify
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
  - Migration: Convert to Ansible playbook for server deployment
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server
  - Migration: Convert to Ansible playbook for server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible assert modules for inline testing
  - Option 2: Use Ansible Molecule for test-driven infrastructure development
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Collections for configuration management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL configuration for Apache. Migration should:
  - Preserve the TLS 1.2 requirement
  - Maintain certificate generation and deployment
  - Ensure proper file permissions for certificates (mode 0640)

- **SSH Security**: The repository includes SSH security tests. Migration should:
  - Maintain SSH root login restrictions
  - Preserve compliance with security benchmarks (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password')
  - Migration should replace these with Ansible Vault for secure credential storage
  - Count of credentials detected: 2 sets in setup scripts (username/password pairs)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Mitigation: Use Ansible's assert module for basic tests, and Molecule for more complex scenarios
  - Consider using community.general.assert_cmd module for command execution testing

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Create Ansible roles for server deployment with idempotent tasks
  - Use Ansible's package management modules instead of curl commands

### Migration Order

1. **InSpec Tests** (Low risk, high value)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Validate that tests still pass against existing infrastructure

2. **Test Kitchen Configuration** (Moderate complexity)
   - Replace Test Kitchen with Ansible Molecule
   - Update test workflows and CI/CD integration

3. **Chef Server Deployment Scripts** (High complexity)
   - Convert Bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are working correctly and don't need modification
2. The primary goal is to replace Chef InSpec testing with Ansible-native solutions
3. The deployment scripts are used for setting up test environments and not production systems
4. The hardcoded credentials in the deployment scripts are for testing purposes only
5. The repository is primarily used for demonstration and educational purposes, as indicated by the README
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There are no external Chef cookbooks or recipes that need migration (only InSpec tests)
8. The migration will maintain the same level of security compliance testing