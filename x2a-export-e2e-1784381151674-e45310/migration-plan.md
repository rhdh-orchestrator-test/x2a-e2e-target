# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test for verifying HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port, HTTP response, and SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification with STIG references

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: molecule for Ansible role/playbook testing
  - Option 2: ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for centralized automation
  - AWX (open source upstream of Ansible Tower) if budget is a concern

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate handlers and idempotent tasks
  
- **SSH Hardening**: The SSH compliance checks need to be preserved
  - Approach: Convert InSpec tests to Ansible assert tasks or ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially with ansible-vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use assert modules in Ansible or consider keeping InSpec as a verification tool called from Ansible
  
- **Compliance Reporting**: Maintaining compliance reporting capabilities without Chef Automate
  - Mitigation: Implement Ansible Automation Platform with compliance capabilities or integrate with a third-party compliance tool

- **Idempotence**: Ensuring all converted scripts maintain idempotence
  - Mitigation: Thorough testing with molecule to verify idempotent behavior

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https role as a security enhancement

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks or maintain as separate InSpec tests called from Ansible

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. There are no external dependencies or integrations not visible in the repository
4. The migration will consolidate to pure Ansible without maintaining Chef components
5. The security compliance requirements (STIG references in ssh_profile.rb) must be preserved in the new solution
6. The Chef Automate and Chef Server deployment scripts are intended for demonstration purposes and not production use