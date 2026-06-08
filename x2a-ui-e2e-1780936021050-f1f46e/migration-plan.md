# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: InSpec tests to verify HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Create an Ansible role for Apache SSL hardening that applies the same configuration

- **SSH Security Hardening**: The SSH compliance checks need to be implemented in Ansible
  - Approach: Create an Ansible role that applies the same SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use assert modules in Ansible to verify configurations, or maintain InSpec as a verification tool called from Ansible

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment
  - Mitigation: Create Ansible roles to deploy alternative compliance and configuration management tools if needed

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Simply review and optimize the existing Ansible playbook

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and incorporate into a comprehensive Apache security role

3. **InSpec Tests** (moderate complexity)
   - Either convert to Ansible assertions or maintain as separate verification tool

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible roles for deploying alternative infrastructure if needed

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There is no requirement to maintain Chef Automate/Server functionality after migration
4. The compliance checks implemented in InSpec are still required in the migrated solution
5. No external data sources or complex state management is required
6. The migration will consolidate all functionality into pure Ansible without Chef components