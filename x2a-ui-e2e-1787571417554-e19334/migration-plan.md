# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains shell scripts and basic Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related shell scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible workflow
  - Replace Test Kitchen with Ansible Molecule for testing
  - Use Ansible's built-in support for InSpec in molecule.yml
  
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative
  - Convert deployment scripts to Ansible roles for infrastructure setup
  - Consider AWX/Ansible Tower for web UI and API functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates
  - Migration should maintain or enhance SSL security settings
  - Consider adding Let's Encrypt integration for proper certificate management

- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Ensure Ansible playbooks maintain SSH security configurations
  - Add Ansible tasks to enforce SSH hardening based on InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration should use Ansible Vault for credential storage
  - Replace hardcoded values with variables stored in encrypted files

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with Ansible-only workflow
  - Solution: Use Ansible Molecule with InSpec verifier or integrate InSpec tests as post-tasks

- **Chef Automate Functionality**: Replacing Chef Automate's functionality with Ansible equivalents
  - Solution: Map Chef Automate features to Ansible Automation Platform or AWX/Tower

- **Testing Framework**: Replacing Test Kitchen with Ansible-native testing
  - Solution: Adopt Molecule for testing Ansible roles and playbooks

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml) - Low risk, already in Ansible format
   - Refactor existing playbooks to follow best practices
   - Convert to roles for better organization
   - Update handlers and variable usage

2. **InSpec Tests** (chef-and-ansible/tests/*.rb) - Medium risk
   - Integrate with Ansible Molecule
   - Ensure tests work with new Ansible structure

3. **Chef Deployment Scripts** (setup-automate/*.sh) - High risk
   - Convert to Ansible roles for infrastructure setup
   - Replace hardcoded values with variables
   - Use Ansible Vault for sensitive data

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment
2. The InSpec tests are essential and must be preserved in the migration
3. The Chef Automate/Infra Server deployment needs to be replaced with equivalent Ansible functionality
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The migration will maintain the same level of security compliance as the original
7. No database or complex application state management is required