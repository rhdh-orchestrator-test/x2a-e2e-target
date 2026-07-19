# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying configurations
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be directly incorporated into the Ansible collection.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening. Can be directly incorporated into the Ansible collection.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Should be converted to Ansible testing framework or kept as InSpec if continuing to use InSpec with Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security. Should be converted to Ansible testing framework or kept as InSpec if continuing to use InSpec with Ansible.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script. Should be replaced with Ansible role for Chef Automate deployment if Chef Automate is still needed.
- `setup-automate/deploy-chef-server.sh`: Chef Server deployment script. Should be replaced with Ansible role for Chef Server deployment if Chef Server is still needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Replace with Ansible-native testing using ansible-test, testinfra, or Molecule
  2. Continue using InSpec as a compliance tool alongside Ansible (recommended if compliance is a key requirement)

- **Test Kitchen**: Used for testing Ansible playbooks. Replace with Molecule for Ansible role/playbook testing.

- **Chef Automate/Infra Server**: Currently deployed via bash scripts. Options:
  1. Replace with Ansible AWX/Tower for similar functionality
  2. Create Ansible roles to deploy Chef Automate/Infra Server if they must be retained
  3. Migrate completely away from Chef infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Maintain proper certificate generation and management
  - Consider using Ansible Vault for sensitive data

- **SSH Hardening**: The SSH InSpec profile checks for root login restrictions. Ensure this security check is maintained in the Ansible implementation.

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates in website_https.yml
  - Recommend implementing Ansible Vault for all credentials

### Technical Challenges

- **Compliance Testing**: If maintaining compliance is critical, decide whether to:
  1. Keep InSpec as a compliance tool and integrate with Ansible workflows
  2. Migrate compliance tests to Ansible-native testing frameworks
  3. Use another compliance tool like OpenSCAP with Ansible

- **Test Kitchen to Molecule Migration**: Converting the testing framework will require recreating test scenarios and verification steps.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Moderate complexity)
   - Convert kitchen.yml to Molecule
   - Decide on compliance testing approach (InSpec or Ansible-native)

3. **Chef Deployment Scripts** (Higher complexity)
   - Replace with Ansible roles or alternative infrastructure

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies where possible.
2. Compliance testing is an important aspect that should be preserved in some form.
3. The repository is primarily for demonstration/example purposes rather than production use.
4. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with proper secret management in production.
5. The self-signed certificates in the website_https.yml playbook would be replaced with proper certificates in production.