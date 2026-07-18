# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration will require replacing with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be directly used in the Ansible migration with minimal changes.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening. Can be directly used in the Ansible migration with minimal changes.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Will need conversion to Ansible testing framework or integration with Ansible via ansible-lint or similar.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Will need conversion to Ansible testing framework or integration with Ansible via ansible-lint or similar.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script. Will need replacement with Ansible playbook for configuration management platform deployment.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script. Will need replacement with Ansible playbook for configuration management platform deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis and compliance checks
  - Option 2: Integrate with Ansible Security Automation for compliance scanning
  - Option 3: Use Molecule for testing Ansible roles with testinfra for verification

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in poodle_fix.yml that disables vulnerable protocols
  - Migration approach: Direct transfer of the existing Ansible task to disable SSLv3 and enable only TLSv1.2

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Preserve the OpenSSL certificate generation tasks or consider integrating with Ansible Vault for certificate management

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled
  - Migration approach: Create equivalent Ansible tasks to verify and enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with equivalent Ansible-native testing capabilities
  - Mitigation: Evaluate ansible-lint, Molecule with testinfra, or maintaining InSpec as a separate tool called from Ansible

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: AWX/Ansible Tower provides similar orchestration capabilities; additional compliance tools may be needed to replace Chef Automate's compliance features

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format
   - Minimal changes needed to integrate with new testing framework

2. **Testing Framework** (chef-and-ansible/tests/*.rb): Moderate complexity
   - Convert InSpec tests to Ansible-compatible testing framework
   - Ensure compliance checks are preserved

3. **Deployment Scripts** (setup-automate/*.sh): High complexity
   - Replace Chef Automate/Infra Server deployment with Ansible Tower/AWX deployment
   - Create Ansible roles for configuration management platform setup

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The SSL and HTTPS configurations are examples rather than production-ready configurations
3. The Chef Automate deployment scripts are for demonstration purposes and contain non-production default credentials
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The migration will standardize on Ansible while preserving the compliance testing capabilities
7. No custom Chef resources or complex Chef-specific functionality is present that would require special handling