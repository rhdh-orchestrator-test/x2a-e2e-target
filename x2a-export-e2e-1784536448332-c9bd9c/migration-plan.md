# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository primarily contains deployment scripts and simple Ansible playbooks rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying and securing Apache web servers with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS configuration. Should be converted to Ansible Molecule tests or maintained as InSpec tests run by Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security configuration. Should be converted to Ansible Molecule tests or maintained as InSpec tests run by Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Replace with Ansible Molecule for testing
  2. Keep InSpec and integrate it with Ansible using the `inspec` Ansible module
  3. Replace with Ansible's built-in assert module for simpler tests

- **Test Kitchen**: Currently used for testing Ansible playbooks. Replace with Ansible Molecule for a more Ansible-native testing approach.

- **Chef Automate/Infra Server**: The deployment scripts need to be replaced with Ansible playbooks that can:
  1. Set up the required system configurations (hostname, sysctl parameters)
  2. Deploy alternative infrastructure management tools (e.g., AWX/Tower, Ansible Automation Platform)
  3. Create equivalent user and organization structures in the new platform

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain or improve these security practices:
  - Self-signed certificate generation
  - Proper file permissions for certificates (mode 0640)
  - TLS protocol version restrictions (disabling SSLv3, enabling TLSv1.2)

- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration should ensure this security check is maintained.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup scripts

### Technical Challenges

- **InSpec Testing Integration**: Determining the best approach to maintain compliance testing while moving to an Ansible-centric workflow:
  - Option 1: Convert InSpec tests to Ansible assertions or Molecule verifiers
  - Option 2: Keep InSpec and integrate it with Ansible using the `inspec` module
  - Mitigation: Start with a proof-of-concept to evaluate both approaches

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality:
  - Option 1: Deploy AWX/Tower as a replacement
  - Option 2: Use Ansible Automation Platform
  - Option 3: Implement a simpler CI/CD pipeline with GitLab/GitHub Actions
  - Mitigation: Assess organization needs and choose the most appropriate solution

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to the new Ansible structure
   - Update testing framework from Test Kitchen to Molecule

2. **Testing Framework** (Medium complexity)
   - Decide on the testing approach (convert InSpec to Ansible assertions or integrate InSpec)
   - Implement the chosen testing approach

3. **Chef Deployment Scripts** (Higher complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The organization is moving completely away from Chef and standardizing on Ansible
2. The InSpec tests are valuable and should be preserved in some form
3. A replacement for Chef Automate/Infra Server functionality is needed
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. The hardcoded credentials in the scripts are for testing only and will be replaced with secure alternatives
7. The Apache configuration and SSL hardening requirements will remain the same
8. The organization has the necessary expertise to maintain Ansible playbooks and testing frameworks