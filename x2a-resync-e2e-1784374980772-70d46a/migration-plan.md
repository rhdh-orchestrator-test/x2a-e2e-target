# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and SSL security compliance
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing with InSpec

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server installation, user/organization creation, automated deployment

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website with Apache, self-signed certificates, and proper SSL configuration. Migration consideration: Can be directly used in Ansible.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening to mitigate POODLE vulnerability. Migration consideration: Can be directly used in Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification, checking port 443 and SSL protocols. Migration consideration: Convert to Ansible test or maintain as InSpec.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance, specifically checking root login settings. Migration consideration: Convert to Ansible test or maintain as InSpec.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script with Chef Infra Server. Migration consideration: Replace with Ansible role for compliance platform deployment.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script without Automate. Migration consideration: Replace with Ansible role for compliance platform deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus (scripts mention "on-prem or cloud VM")

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Ansible Molecule or maintain InSpec as a standalone compliance tool
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with alternative compliance platforms like:
  - Ansible Automation Platform for orchestration
  - OpenSCAP or Compliance as Code for compliance scanning
  - AWX/Tower for workflow management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates and explicitly disable SSLv3 while enabling TLSv1.2 to mitigate POODLE vulnerability. Migration should maintain or improve this security practice.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. This security check should be preserved in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: jtonello, password: password)
  - SSL certificate generation and management
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Compliance Testing**: Deciding whether to maintain InSpec for testing or migrate to Ansible-native testing solutions. Mitigation: Could maintain InSpec as a specialized compliance tool or implement equivalent tests in Ansible.
- **Deployment Architecture**: The current setup deploys Chef Automate for compliance. Mitigation: Design an equivalent Ansible-based compliance architecture.

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. Testing framework (kitchen.yml, InSpec tests) - moderate complexity
3. Chef Automate/Server deployment scripts - high complexity, requires architectural decisions

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation alongside infrastructure provisioning.
2. The InSpec tests are considered valuable and should be preserved in some form.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The deployment scripts are examples and not production-ready (contain hardcoded credentials).
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The migration will consolidate all infrastructure provisioning into Ansible while maintaining compliance capabilities.