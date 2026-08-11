# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The repository appears to be primarily educational in nature, showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The main challenge will be replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, service restart handlers

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that verifies SSH security compliance (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

- **automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file for the website. Migration consideration: Can be directly used in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider OpenSCAP integration for STIG compliance

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Consider these alternatives:
  - AWX/Ansible Tower for enterprise automation platform
  - Ansible Semaphore for lightweight GUI
  - GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2+ is enforced (currently done in poodle_fix.yml)
  - Consider adding modern cipher suites
  - Add option for Let's Encrypt integration instead of self-signed certificates

- **SSH Hardening**: The InSpec tests verify SSH security. Migration should include:
  - Ansible tasks to enforce SSH hardening
  - Equivalent compliance checks using Ansible assertions

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests will require careful mapping of test logic
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.assert with appropriate conditions

- **Deployment Script Conversion**: The Chef Automate/Server deployment scripts need to be converted to Ansible roles
  - Mitigation: Create dedicated roles for infrastructure components
  - Use Ansible Galaxy to find existing roles for Chef server deployment if needed

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add idempotency improvements if needed
   - Convert to a proper Ansible role structure

2. **poodle-fix playbook** (low risk, already Ansible)
   - Integrate with the website-https role
   - Expand to cover additional security hardening

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Deployment scripts** (high complexity)
   - Convert to Ansible roles
   - Implement Ansible Vault for credential management
   - Consider if Chef Automate/Server is still needed or can be replaced

### Assumptions

1. The repository is primarily educational/demonstrative and not used in production
2. The InSpec tests are used for compliance validation only and not for active remediation
3. The deployment scripts are examples and may need customization for actual environments
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There's no existing Ansible inventory or group_vars structure
6. The migration will maintain the same functionality but in pure Ansible
7. No external dependencies or integrations beyond what's visible in the repository