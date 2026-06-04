# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks with Chef InSpec tests for compliance validation
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure automation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-website-tests**:
    - Description: Chef InSpec tests that validate HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol security verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file used for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with ansible-test for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for integration testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain the same level of Apache security configuration

- **SSH Security**: Preserve the SSH root login security check
  - Convert InSpec test to equivalent Ansible assert or ansible-lint rule

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 2 credentials detected (username/password in deploy scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible assert modules or custom modules to perform the same validation checks
  - Consider maintaining InSpec as a separate tool if complex compliance requirements exist

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible automation
  - Mitigation: Create Ansible roles for configuration management server deployment
  - Consider if Chef server is still needed or if migration to pure Ansible is preferred

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle-fix playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https role as a security hardening task

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or maintain as separate InSpec tests
   - Ensure integration with Ansible testing workflow

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace Chef server deployment
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies where possible
2. InSpec tests may need to be maintained if equivalent Ansible testing capabilities are insufficient
3. The deployment scripts are used for setting up test environments and not production systems
4. The hardcoded credentials in deployment scripts are for demonstration purposes only
5. The repository is primarily educational/demonstration content rather than production code
6. The Apache configuration is relatively simple and can be directly migrated to Ansible roles
7. No complex Chef cookbooks or recipes are present that would require significant refactoring