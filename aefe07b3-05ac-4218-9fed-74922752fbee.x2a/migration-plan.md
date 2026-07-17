# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-compatible testing frameworks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks and InSpec tests for web server deployment and compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache configuration, SSL certificate generation, compliance testing

- **setup-automate**:
    - Description: Module containing bash scripts for Chef Automate and Chef Infra Server deployment
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/website_https.yml`: Ansible playbook for setting up Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security configuration
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for compliance testing
  - Option 3: Use ansible-lint for static analysis and basic compliance

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Ansible Test for integration testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable SSL protocols

- **SSH Security**: The SSH security checks in ssh_profile.rb need to be implemented in the new testing framework
  - Root login restrictions
  - Compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - No encrypted secrets detected in the repository
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework
  - Challenge: InSpec has specific syntax for compliance testing that needs to be mapped to equivalent assertions in the target framework
  - Mitigation: Create a mapping document for InSpec resources to Testinfra or other testing framework equivalents

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation of Chef components
  - Mitigation: Use Ansible's package management and service modules with appropriate state checks

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible module)
   - Low risk as these are already in Ansible format
   - May need minor updates for compatibility with newer Ansible versions

2. **InSpec Tests** (chef-and-ansible/tests directory)
   - Convert to Molecule with Testinfra or equivalent
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (setup-automate module)
   - Convert to Ansible playbooks
   - Implement secret management with Ansible Vault

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while preserving the compliance testing functionality
2. The existing Ansible playbooks are compatible with current Ansible versions and don't require significant updates
3. The deployment scripts are used for setting up test environments and not production systems
4. No external Chef cookbooks or recipes are being used that would need migration
5. The repository is primarily for demonstration purposes as indicated by the README
6. No complex data structures or custom facts are being used that would require special handling
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions