# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and integrating the Chef InSpec tests into an Ansible-native testing framework.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance checks

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization setup

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a template for the website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Maintain InSpec as a testing tool but integrate with Ansible workflows
  - Option 3: Convert InSpec tests to Ansible assert tasks for simple checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and management
  - Ansible Collections for configuration management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL that follows current best practices

- **SSH Hardening**: The InSpec tests check for SSH security configurations.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same security controls

- **Self-signed Certificates**: The current implementation uses self-signed certificates.
  - Migration approach: Consider integrating with Let's Encrypt for production environments or maintain self-signed certificates for development

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing frameworks may require additional effort.
  - Mitigation: Consider using Ansible's assert module for simple tests or maintain InSpec for complex compliance testing

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem.
  - Mitigation: AWX/Ansible Tower provides similar functionality for orchestration and management

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Implement idempotency improvements
   - Add documentation

2. **poodle-fix playbook** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Combine with website-https role as an optional feature

3. **InSpec tests** (medium complexity)
   - Option 1: Convert to Ansible Molecule with testinfra
   - Option 2: Maintain as InSpec tests but integrate with Ansible workflow

4. **Chef Automate/Server setup scripts** (high complexity)
   - Convert to Ansible roles for setting up AWX/Ansible Tower
   - Create documentation for migration path from Chef to Ansible

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec tests are valuable and should be preserved in some form
3. The Chef Automate and Chef Infra Server setup scripts are used for setting up a Chef environment, which would be replaced by an Ansible environment
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The security requirements demonstrated in the InSpec tests (SSH hardening, SSL configuration) are important to maintain
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data structures or custom facts are being used
8. No existing Ansible inventory or group variables are present