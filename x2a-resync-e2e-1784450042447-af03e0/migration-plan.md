# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks with InSpec tests that need to be consolidated into a pure Ansible solution. The migration scope includes two main components:

1. Chef Automate and Chef Infra Server deployment scripts (Bash)
2. Ansible playbooks for configuring Apache web servers with SSL and InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents, and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring Apache web servers with SSL and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache SSL configuration, self-signed certificate generation, compliance testing with InSpec, Test Kitchen integration

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation, credential management

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing or adapt to use Ansible's native integration with InSpec.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with SSL. Migration consideration: Can be used as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities (POODLE). Migration consideration: Can be used as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Integrate with Ansible's testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Integrate with Ansible's testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or alternative infrastructure management
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **InSpec**: Either integrate with Ansible via ansible_inspec module or replace with Ansible's native compliance capabilities
- **Apache2**: Continue using Ansible's apt module for installation and configuration

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (poodle_fix.yml) that must be preserved in the migration
- **Self-signed Certificates**: The current implementation generates self-signed certificates; consider integrating with Let's Encrypt for production environments
- **SSH Security**: InSpec tests verify SSH security configurations; ensure these compliance checks are maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count: 2 credential sets identified (user login, SSL certificates)

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the Ansible-only solution
  - Mitigation: Use the ansible_inspec module or convert InSpec tests to Ansible assertions
- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Consider Ansible AWX/Tower for web UI and control, or other infrastructure management tools
- **Compliance Testing**: Maintaining the same level of compliance testing without Chef InSpec
  - Mitigation: Use Ansible's built-in assert module or integrate with other compliance tools

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **InSpec Tests** (Moderate complexity)
   - Integrate or convert InSpec tests to work with Ansible

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Infra Server deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There are no external dependencies or integrations not visible in the repository
5. The migration will maintain the same level of security compliance testing
6. The Chef Automate and Chef Infra Server functionality needs to be replaced with equivalent Ansible-based solutions