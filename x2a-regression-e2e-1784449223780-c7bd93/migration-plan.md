# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and InSpec tests demonstrating compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible and Chef InSpec
    - Key Features: HTTPS website configuration, SSL hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that remediates the POODLE vulnerability
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Ansible's community.general.inspec module to continue using InSpec tests
  - Option 4: Migrate to Ansible Automation Platform with built-in compliance capabilities

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the migrated Ansible roles
  - Consider enhancing with more modern TLS best practices (TLS 1.3 support)

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Consider enhancing with Let's Encrypt integration for production environments
  - Maintain proper certificate permissions and security

- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH security
  - Ensure SSH hardening is included in the migrated Ansible roles
  - Consider using the ansible-hardening role for comprehensive SSH security

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with Ansible-native testing
  - Challenge: InSpec provides rich compliance testing capabilities
  - Mitigation: Use ansible-lint and assert modules for basic checks, or maintain InSpec via the community.general.inspec module

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible
  - Challenge: The deployment scripts contain Chef-specific commands and configurations
  - Mitigation: Create Ansible roles that install and configure Chef components if still needed, or replace with Ansible Automation Platform

### Migration Order

1. **Ansible playbooks in chef-and-ansible directory** (low risk, already in Ansible)
   - Refactor website_https.yml and poodle_fix.yml into proper Ansible roles with variables
   - Enhance with modern best practices

2. **InSpec test profiles in chef-and-ansible/tests directory** (moderate complexity)
   - Convert to Ansible assert tasks or maintain using community.general.inspec module
   - Ensure all compliance checks are preserved

3. **Chef deployment scripts in setup-automate directory** (high complexity)
   - Replace with Ansible roles for Chef deployment if Chef is still needed
   - Or replace with Ansible Automation Platform setup if moving away from Chef entirely

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining compliance capabilities
2. Chef InSpec tests are valuable and need to be preserved in some form
3. The Chef Automate and Chef Server deployment may be replaced entirely with Ansible Automation Platform
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (SSL/TLS hardening, SSH security) must be maintained
7. The repository is primarily for demonstration/educational purposes rather than production use
8. No external dependencies or integrations beyond what's visible in the repository