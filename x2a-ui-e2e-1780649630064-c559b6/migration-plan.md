# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance validation
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS, self-signed certificates, and a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test profile that validates HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (specifically root login settings)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation with STIG compliance metadata

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a template for website deployment

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Use Molecule for Ansible role testing
  - Option 2: Create custom Ansible playbooks for test environment provisioning

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower
  - Option 2: Use Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache SSL hardening that implements the same security controls

- **SSH Security**: The SSH compliance checks must be maintained
  - Approach: Convert InSpec SSH tests to Ansible assert statements or Ansible-lint custom rules

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in deploy scripts

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Create custom Ansible modules or use assert statements to replicate InSpec functionality
  - Consider maintaining InSpec as a separate tool called from Ansible if direct conversion is too complex

- **Test Kitchen Integration**: Replacing Test Kitchen workflow
  - Mitigation: Implement Molecule testing framework which is designed for Ansible role testing

- **Chef Server Deployment**: Replacing Chef server deployment scripts
  - Mitigation: This is likely out of scope for the migration as the purpose would be to move away from Chef infrastructure

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Convert to Ansible role structure for better reusability

2. **poodle-fix playbook** (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Integrate with website-https role as an optional security enhancement

3. **InSpec test profiles** (moderate complexity)
   - Convert to Ansible assert statements or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity, likely out of scope)
   - Determine if these need to be migrated or are no longer needed
   - If needed, create Ansible playbooks for equivalent infrastructure deployment

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies
2. InSpec tests are valuable and their functionality should be preserved
3. The Chef Automate/Infra Server deployment scripts may be out of scope if the target environment will not use Chef
4. The repository is primarily for demonstration purposes rather than production use
5. The hardcoded credentials in the deployment scripts are examples and not actual production credentials
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The SSL/TLS security requirements (TLSv1.2, no SSLv3) must be maintained in the migrated solution