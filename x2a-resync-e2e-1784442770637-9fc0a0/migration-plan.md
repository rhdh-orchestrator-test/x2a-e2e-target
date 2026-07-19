# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The primary components are:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for web server configuration with InSpec testing
3. Chef InSpec profiles for compliance testing

The migration complexity is **LOW to MEDIUM** as most of the repository already contains Ansible playbooks. The main effort will be in converting the Chef Automate and Chef Infra Server deployment scripts to Ansible roles and integrating the InSpec testing framework with Ansible. Estimated timeline: **2-3 weeks** for a small team.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing for HTTPS and SSH

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly reused in the migrated solution.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Can be directly reused in the migrated solution.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be integrated with Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be integrated with Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing or integrate InSpec with Ansible using the `inspec` Ansible module
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening in `poodle_fix.yml` that disables SSLv3 and only enables TLSv1.2
- **SSH Hardening**: The SSH security profile in `ssh_profile.rb` must be maintained in the Ansible implementation
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - SSL certificates generated in the Ansible playbook should use secure key management
  - Count of credentials detected: 5 (username, longusername, useremail, userpassword, orgname in deployment scripts)

### Technical Challenges

- **InSpec Integration**: Ensuring that the InSpec tests continue to work with the Ansible-only solution. Mitigation: Use the Ansible `inspec` module to run InSpec tests as part of playbook execution.
- **Chef Automate Replacement**: Determining the appropriate Ansible management platform to replace Chef Automate functionality. Mitigation: Evaluate Ansible AWX/Tower or other Ansible management solutions.
- **Testing Framework**: Replacing Test Kitchen with an Ansible-native testing framework. Mitigation: Implement Molecule for testing Ansible roles.
- **Self-signed Certificates**: Ensuring proper handling of self-signed certificates in the Ansible implementation. Mitigation: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Migrate `website_https.yml` and `poodle_fix.yml` to Ansible roles
2. **InSpec Tests** (Medium complexity): Integrate InSpec tests with Ansible using the `inspec` module
3. **Chef Deployment Scripts** (High complexity): Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks

### Assumptions

1. The current repository is used for demonstration/example purposes rather than production, as indicated by the README.md.
2. The Chef Automate and Chef Infra Server deployment is intended for on-premises or generic cloud VMs.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
4. The InSpec tests are essential to the compliance strategy and must be maintained in the Ansible migration.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
6. Vagrant is used for local development and testing, but the production environment may differ.
7. The migration will consolidate all configuration management to Ansible, eliminating the need for Chef components except possibly InSpec for testing.
8. The Apache web server configuration is a critical component that must be preserved with the same security settings.
9. The SSL/TLS security hardening is a compliance requirement that must be maintained in the Ansible implementation.