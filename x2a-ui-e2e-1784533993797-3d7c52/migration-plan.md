# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks with minor improvements
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring proper integration between components

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should maintain test capabilities using Ansible's molecule or similar testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Can be preserved with minor improvements.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be preserved with minor improvements.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment. Can be preserved as-is.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Can be preserved as-is.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Needs conversion to Ansible playbook.

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml and package versions in the Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (for development/testing based on kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Maintain as a compliance testing tool, integrated with Ansible workflows
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance these security settings.
- **SSH Security**: InSpec tests validate SSH root login is disabled. Migration should ensure this security practice is maintained.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL/TLS certificate references in the Apache configuration

### Technical Challenges

- **Chef InSpec Integration**: Ensuring proper integration between Ansible and Chef InSpec for compliance testing. Mitigation: Use Ansible's built-in capabilities to run InSpec tests or consider migrating to Ansible's native compliance capabilities.
- **Chef Automate Functionality**: Determining if all Chef Automate functionality is needed or if it can be replaced with simpler Ansible-based solutions. Mitigation: Analyze current usage patterns and identify core requirements.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible): Review and enhance existing playbooks with best practices
2. **Chef Deployment Scripts** (Moderate complexity): Convert bash scripts to Ansible playbooks
3. **Testing Framework** (Moderate complexity): Replace Test Kitchen with Ansible Molecule while preserving InSpec tests

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments (based on README.md content).
2. Chef InSpec is still desired for compliance testing even after migration to Ansible.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure alternatives in production.
4. The target environment is Ubuntu 20.04 LTS, but the solution should be adaptable to other distributions.
5. The self-signed certificates are acceptable for the use case, but production deployments might require proper CA-signed certificates.
6. The repository does not contain actual Chef cookbooks or recipes that need migration, only deployment scripts for Chef infrastructure.