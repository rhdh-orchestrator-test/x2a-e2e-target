# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer. The repository appears to be primarily educational/demonstration content rather than production infrastructure code.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no Puppet modules (no manifests/init.pp files), no Chef cookbooks (no recipes/default.rb files), and no PowerShell modules (no .psd1 files) in this repository. The repository primarily contains Ansible playbooks and bash scripts.

- **website_https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **deploy-automate**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate deployment, Chef Server deployment, user/organization setup

- **deploy-chef-server**:
    - Description: Bash script for deploying Chef Infra Server only
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server deployment, user/organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, as it's compatible with Ansible
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible playbooks
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative CI/CD solution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache, which needs to be preserved
  - Migration approach: Maintain the same SSL configuration in Ansible playbooks
  
- **SSH Security**: InSpec tests validate SSH root login restrictions
  - Migration approach: Maintain InSpec tests and ensure Ansible playbooks enforce the same SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

1. **Chef InSpec Integration**: 
   - Description: Maintaining InSpec tests while migrating to pure Ansible
   - Mitigation: Keep InSpec for compliance testing, which works well with Ansible

2. **Chef Automate Replacement**:
   - Description: Finding equivalent functionality in Ansible ecosystem
   - Mitigation: Consider Ansible Automation Platform or integrate with other CI/CD tools

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format
   - Update and optimize existing Ansible playbooks
   - Replace Test Kitchen with Ansible Molecule for testing

2. **Chef Automate Scripts** (setup-automate/*.sh): Medium complexity
   - Convert Bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production infrastructure
2. Chef InSpec will continue to be used for compliance testing alongside Ansible
3. The hardcoded credentials in the setup scripts are not for production use
4. The target environment will continue to be Ubuntu 20.04 or similar
5. The existing Ansible playbooks are functional and follow best practices
6. No external dependencies or third-party modules are required beyond what's visible in the repository