# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: Chef InSpec profile that validates HTTPS website configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **ssh-security-compliance**:
    - Description: Chef InSpec profile that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening that disables vulnerable protocols
  - Migration approach: Convert the SSL configuration to an Ansible role with appropriate templates and handlers

- **SSH Hardening**: The SSH security compliance checks need to be maintained
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed through Ansible's crypto modules

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing functionality currently provided by InSpec
  - Mitigation: Either maintain InSpec as a separate tool or implement equivalent checks using Ansible's assert module and Molecule

- **Test Kitchen to Molecule**: Converting the test workflow from Test Kitchen to Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to a proper Ansible role with variables, templates, and handlers

2. **poodle-ssl-fix** (low risk, already in Ansible)
   - Integrate into the website HTTPS role as a configurable option

3. **Compliance Testing** (moderate complexity)
   - Either maintain InSpec tests or convert to Ansible/Molecule tests

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles for deploying Chef infrastructure if still needed
   - Alternatively, replace with pure Ansible infrastructure management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than to provide production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. The compliance testing requirements will remain the same
4. There is no requirement to maintain Chef Automate or Chef Infra Server after migration
5. The migration will consolidate all infrastructure provisioning into Ansible while preserving compliance testing capabilities