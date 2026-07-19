# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to medium, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **ansible-web-deployment**:
    - Description: Ansible playbooks for secure Apache web server deployment with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL security configuration, self-signed certificate generation, compliance testing

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL vulnerabilities in Apache. Migration considerations include ensuring the security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec testing. Will need to be updated for pure Ansible testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Consider migrating to Ansible test framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Consider migrating to Ansible test framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Will need to be replaced with Ansible roles for configuration management.
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server. Will need to be replaced with Ansible roles for configuration management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible testing frameworks like Molecule or maintain InSpec as a testing tool while standardizing on Ansible for configuration management
- **Test Kitchen**: Replace with Ansible-native testing frameworks or adapt for pure Ansible usage
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for enterprise management or use alternative compliance tools

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS protocols (disabling SSLv3, enabling TLSv1.2)
- **Certificate Management**: Self-signed certificate generation must be preserved or improved
- **SSH Hardening**: SSH security controls (disabling root login) must be maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain Chef InSpec for testing or migrate to Ansible-native testing tools
- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server deployment scripts with equivalent Ansible roles
- **Test Framework**: Adapting the testing framework from Test Kitchen to an Ansible-native approach

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible): Standardize and optimize existing Ansible playbooks
2. **InSpec Tests** (Moderate complexity): Either maintain as-is or migrate to Ansible testing framework
3. **Chef Deployment Scripts** (High complexity): Replace with Ansible roles for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef components (Automate, Infra Server) are not critical to the functionality of the Ansible playbooks
3. The compliance testing functionality is important to preserve, whether using InSpec or an alternative
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment will continue to use self-signed certificates rather than requiring integration with a certificate authority
6. No external data sources or databases are required for the application
7. No complex orchestration or scheduling is needed beyond what Ansible provides natively