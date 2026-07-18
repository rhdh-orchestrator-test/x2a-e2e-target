# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is focused on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while integrating them into a cohesive Ansible structure
3. Maintaining Chef InSpec tests for compliance verification while integrating them with Ansible

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most functionality already in Ansible

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec tests but integrate with Ansible using ansible_inspec module or ansible-lint

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols (SSL3). This security hardening should be preserved in the migrated Ansible roles.
- **SSH Security**: InSpec tests verify SSH root login is disabled. This compliance check should be maintained.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider using Let's Encrypt or other trusted certificates in production.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count: 2 credential sets detected (user credentials in both setup scripts)

### Technical Challenges

- **Chef InSpec Integration**: While migrating to pure Ansible, maintain the InSpec tests for compliance verification. This can be achieved using the ansible_inspec module or by calling InSpec directly from Ansible tasks.
- **Chef Automate Replacement**: Determine if Chef Automate functionality needs to be replaced with an alternative solution (e.g., AWX/Tower, Ansible Semaphore) or if it's no longer needed.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Reorganize existing Ansible playbooks into proper roles and structure
   - Integrate InSpec tests with Ansible using ansible_inspec module

2. **Chef Deployment Scripts** (Medium complexity)
   - Convert bash scripts to Ansible roles for deploying configuration management tools
   - Consider if Chef Automate/Infra Server is still needed or can be replaced with Ansible Tower/AWX

### Assumptions

1. The repository appears to be a demonstration/example repository rather than production code, based on the README.md content.
2. The Chef components (Automate, Infra Server) are being used for infrastructure management that will be replaced by Ansible.
3. InSpec tests are still valuable for compliance verification and should be preserved.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in production.
6. The migration is focused on moving away from Chef while maintaining or enhancing the security compliance capabilities provided by InSpec.