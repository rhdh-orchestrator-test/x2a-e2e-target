# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-compliance**:
    - Description: Chef InSpec profile for validating HTTPS website configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS response validation, SSL protocol security checks

- **ssh-security-compliance**:
    - Description: Chef InSpec profile for validating SSH security configuration
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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are maintained in the migrated Ansible roles
  - Consider enhancing with more comprehensive TLS hardening based on current best practices

- **SSH Security**: The SSH compliance checks must be preserved
  - Convert the InSpec SSH profile to equivalent Ansible assertions or ansible-lint rules
  - Ensure the STIG compliance metadata is preserved for audit purposes

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use assert modules in Ansible or consider maintaining InSpec as a verification layer

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Mitigation: Document compliance mappings and ensure they're represented in Ansible roles

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Convert to a proper Ansible role with variables
   - Enhance with best practices for Apache configuration

2. **poodle-ssl-fix** (low risk, already in Ansible)
   - Integrate into the Apache role as a security hardening option
   - Update to include additional modern TLS best practices

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or maintain as separate verification layer
   - Ensure compliance metadata is preserved

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles for deploying compliance tools
   - Consider if Chef Automate/Server is still needed or if it can be replaced with Ansible Automation Platform

### Assumptions

1. The primary goal is to consolidate on Ansible while maintaining compliance capabilities
2. The InSpec tests are valuable and need to be preserved in some form
3. The deployment scripts for Chef infrastructure may be deprecated if moving entirely to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security hardening requirements (STIG compliance) must be maintained
7. The repository is primarily for demonstration/educational purposes rather than production use