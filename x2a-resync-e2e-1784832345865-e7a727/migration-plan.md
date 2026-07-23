# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be a demonstration environment showing how Chef InSpec can be used alongside Ansible for compliance automation. The main components include:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to convert. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components and moderate complexity for converting the InSpec tests to Ansible-native testing solutions.

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
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

- **chef-automate-deploy**:
    - Description: Shell script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Simple HTML content for the test website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles
  - Option 2: Ansible Assert module for inline testing
  - Option 3: Maintain separate InSpec tests but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing
  - Or maintain Test Kitchen but use the Ansible verifier instead of InSpec

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for deploying alternative compliance and configuration management solutions
  - Consider migrating to Ansible Tower/AWX for enterprise features

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible tasks directly to the new Ansible structure
  
- **SSH Hardening**: The SSH security tests must be converted to equivalent Ansible checks
  - Approach: Use Ansible assert module or Molecule to verify SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely in the new implementation

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  
- **Compliance Validation**: Ensuring the same level of compliance validation in Ansible as provided by InSpec
  - Mitigation: Consider using ansible-lint with custom rules or maintaining InSpec alongside Ansible

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow with an Ansible-native testing approach
  - Mitigation: Implement Molecule testing with similar VM provisioning capabilities

### Migration Order

1. **website-https.yml** (low risk, already Ansible)
   - Minimal changes needed, just standardize with best practices
   
2. **poodle-fix.yml** (low risk, already Ansible)
   - Minimal changes needed, just standardize with best practices
   
3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible testing framework
   - Ensure all compliance checks are maintained
   
4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for alternative solutions
   - Consider if Chef Automate/Server is still needed or can be replaced

### Assumptions

1. The primary goal is to migrate all components to pure Ansible, eliminating Chef dependencies
2. The InSpec tests are valuable and their functionality should be preserved in the Ansible solution
3. The deployment scripts for Chef Automate/Server may be replaced with equivalent Ansible automation or removed entirely
4. The target environment (Ubuntu 20.04 on Vagrant) will remain the same after migration
5. No external dependencies or integrations beyond what's visible in the repository
6. The security and compliance requirements represented in the InSpec tests must be maintained
7. The repository is primarily for demonstration/educational purposes rather than production use