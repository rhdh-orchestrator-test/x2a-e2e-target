# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL/TLS configuration and InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace this with Ansible-native testing solutions like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. This can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. This can be directly incorporated into the new Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS configuration. Should be migrated to Ansible-native testing or maintained as a separate compliance validation layer.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be migrated to Ansible-native testing or maintained as a separate compliance validation layer.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain as a separate compliance validation layer
- **Test Kitchen**: Replace with Ansible-native testing solutions like Molecule
- **Chef Automate/Infra Server**: Determine if these need to be deployed in the new environment or if they're being replaced entirely by Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the secure TLS 1.2 configuration and disable vulnerable protocols (SSL3)
- **SSH Security**: The SSH hardening profile must be maintained in the new Ansible implementation
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider implementing proper certificate management
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should use Ansible Vault or external certificate management

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain Chef InSpec for compliance testing or migrate to Ansible-native solutions
- **Certificate Management**: Implementing proper certificate management instead of self-signed certificates
- **Idempotency**: Ensuring all converted scripts maintain idempotency in Ansible

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk, already in Ansible format
2. **Chef Deployment Scripts** (setup-automate): Medium complexity, requires conversion from Bash to Ansible
3. **Testing Framework** (InSpec tests): Medium complexity, requires decision on testing strategy

### Assumptions

1. The Chef Automate and Chef Infra Server deployment is being replaced by Ansible, not just the deployment method
2. The existing Ansible playbooks are functional and can be incorporated into the new structure with minimal changes
3. The InSpec tests are valuable and should be maintained in some form
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure credential management
6. The self-signed certificates are for testing only and will be replaced with proper certificate management in production