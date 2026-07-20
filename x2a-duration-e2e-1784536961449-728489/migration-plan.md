# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks with minor improvements
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring proper integration between components

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains straightforward deployment scripts and Ansible playbooks

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved with minor improvements.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Can be preserved with minor improvements.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment. Can be preserved for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Can be preserved for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to Ansible playbook.

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as a compliance testing tool, integrate with Ansible workflows
- **Test Kitchen**: Replace with Molecule for Ansible-native testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. Migration should maintain or enhance these security practices.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration should maintain this security practice.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates in website_https.yml
  - Migration should implement Ansible Vault for credential management

### Technical Challenges

- **Chef InSpec Integration**: Ensuring continued integration between Ansible and Chef InSpec for compliance testing. Mitigation: Use Ansible's built-in capabilities to run InSpec tests.
- **Chef Automate Replacement**: Determining if Chef Automate functionality needs to be replaced or if it's just used for demonstration. Mitigation: Clarify requirements with stakeholders.

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, already in Ansible format)
   - Enhance with Ansible best practices
   - Implement Ansible Vault for secrets
   - Replace Test Kitchen with Molecule

2. **setup-automate Bash Scripts** (moderate complexity)
   - Convert to Ansible playbooks
   - Implement Ansible Vault for credentials
   - Create roles for Chef Automate and Chef Infra Server deployment

3. **Testing Framework** (low complexity)
   - Maintain InSpec tests
   - Integrate with Ansible workflows

### Assumptions

1. The repository appears to be primarily for demonstration/educational purposes rather than production use, based on the README.md content.
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be migrated to Ansible, not just preserved.
3. The existing Ansible playbooks should be maintained but enhanced with best practices.
4. Chef InSpec will continue to be used for compliance testing, even after migration to Ansible.
5. The hardcoded credentials in the setup-automate scripts are for demonstration purposes and will be replaced with Ansible Vault.
6. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be flexible enough for other environments.