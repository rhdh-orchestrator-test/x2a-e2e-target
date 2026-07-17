# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for HTTPS website deployment with Chef InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website configuration, SSL security hardening, compliance testing with InSpec

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with equivalent Ansible testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality. Migration considerations include converting to Ansible-compatible testing or maintaining InSpec as a testing tool.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance. Migration considerations include converting to Ansible-compatible testing or maintaining InSpec as a testing tool.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in setup-automate script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Ansible Molecule or maintain InSpec as a standalone testing tool integrated with Ansible workflows
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management or eliminate if not needed

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook, specifically enforcing TLSv1.2 and disabling vulnerable protocols
- **SSH Security**: The SSH compliance profile checks must be preserved, particularly the root login restrictions
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for storing private keys

### Technical Challenges

- **Compliance Testing**: Determining whether to maintain Chef InSpec as a testing tool or migrate to Ansible-native testing solutions. InSpec provides robust compliance testing capabilities that may not be fully replicated in Ansible-native tools.
  - Mitigation: Consider a hybrid approach where Ansible handles all infrastructure provisioning but InSpec is still used for compliance testing, invoked by Ansible.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality.
  - Mitigation: Evaluate Ansible AWX/Tower as a replacement for centralized management and reporting.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format, just need review and potential refactoring to follow best practices
2. **Testing Framework** (chef-and-ansible/tests): Moderate complexity, requires decision on whether to maintain InSpec or migrate to Ansible-native testing
3. **Chef Deployment Scripts** (setup-automate): High complexity, requires complete rewrite as Ansible roles/playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec compliance testing alongside Ansible, not to provide production-ready infrastructure code.
2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration purposes and may not reflect production deployment practices.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in a production environment.
4. The repository is intended for educational/demonstration purposes rather than production use, as indicated by the README.md mentioning it's related to content created by Technical Product Marketing and Developer Relations teams.
5. The target audience is users interested in learning how to use Chef InSpec with Ansible for compliance automation.
6. The compliance profiles are examples and may need to be expanded for comprehensive security coverage in production environments.