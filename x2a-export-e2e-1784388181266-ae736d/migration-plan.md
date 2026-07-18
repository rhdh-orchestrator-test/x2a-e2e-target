# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring the migration preserves the security and compliance testing capabilities

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for deploying and validating a secure HTTPS website
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with equivalent Ansible testing framework or adapting to use InSpec with pure Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality. Should be preserved as-is for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be preserved as-is for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include converting to Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include converting to Ansible playbook for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version 2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as a compliance testing tool alongside Ansible. No direct replacement needed as InSpec works well with Ansible.
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks, while maintaining the ability to use InSpec for verification.
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can deploy alternative infrastructure management solutions or maintain Chef deployment if required.

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in `poodle_fix.yml` that disables SSLv3 and enables TLSv1.2.
- **Self-signed Certificates**: The migration must maintain the secure generation of SSL certificates for Apache.
- **SSH Security**: The InSpec profile for SSH security testing must be preserved to ensure continued compliance validation.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef deployment scripts contain hardcoded usernames and passwords that should be moved to Ansible Vault.
  - SSL/TLS certificate references: The Apache configuration references SSL certificate files that should be handled securely.

### Technical Challenges

- **Maintaining InSpec Integration**: Ensuring that Chef InSpec tests continue to work seamlessly with the migrated Ansible playbooks. Mitigation: Use Ansible's built-in integration with InSpec or implement a post-deployment testing phase.
- **Chef Automate/Infra Server Replacement**: Determining if Chef Automate/Infra Server should be replaced with an Ansible-native solution or if the deployment scripts should simply be converted to Ansible. Mitigation: Assess the organization's needs for infrastructure management and compliance reporting.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible): Preserve existing Ansible playbooks (`website_https.yml`, `poodle_fix.yml`) with minimal changes.
2. **InSpec Tests** (Low risk): Preserve InSpec tests as-is, ensuring they work with the migrated infrastructure.
3. **Chef Deployment Scripts** (Moderate complexity): Convert the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks.
4. **Testing Framework** (Moderate complexity): Replace Test Kitchen with Ansible Molecule while maintaining InSpec for verification.

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool while maintaining the compliance testing capabilities of Chef InSpec.
2. The existing Ansible playbooks are working correctly and don't require significant modifications beyond standardization.
3. The organization may still need Chef Automate/Infra Server for other purposes not evident in this repository, so the migration should provide equivalent deployment capabilities using Ansible.
4. The hardcoded credentials in the Chef deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The InSpec tests are considered valuable and should be preserved rather than converted to Ansible-native testing tools.