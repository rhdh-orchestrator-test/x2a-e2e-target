# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components:

1. A set of Ansible playbooks with Chef InSpec tests for compliance verification
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating everything into pure Ansible.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for compliance verification of web servers
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL/TLS configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration will require replacing with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Will need conversion to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need conversion to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Will need replacement with Ansible roles for compliance tooling.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need replacement with Ansible roles for compliance tooling.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance testing using one of:
  - Ansible Lint for static code analysis
  - ansible-test for integration testing
  - Molecule for comprehensive testing
  - OpenSCAP with Ansible for compliance scanning

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Collections for compliance profiles (replacing InSpec profiles)

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migration.
  - Migration approach: Maintain the same SSL configuration in the Ansible playbooks

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in playbooks
  - Migration approach: Replace with Ansible Vault for credential storage and implement certificate management using Ansible modules

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with Ansible-native testing.
  - Mitigation: Use Ansible's assert module for basic tests and integrate with tools like OpenSCAP for more complex compliance testing

- **Test Framework**: Replacing Test Kitchen with Molecule will require reconfiguration of test environments.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Migrate `website_https.yml` and `poodle_fix.yml` with minimal changes
2. **Compliance Tests** (Moderate complexity): Convert InSpec tests to Ansible-native testing
3. **Chef Server Deployment** (High complexity): Replace Chef Automate/Infra Server scripts with Ansible roles for compliance tooling

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance testing alongside configuration management
2. The Chef InSpec tests are the critical component to preserve in functionality
3. There are no external dependencies on Chef Automate beyond what's in the deployment scripts
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external data sources or integrations are required beyond what's visible in the repository
6. The hardcoded credentials in the setup scripts are for demonstration purposes only
7. The self-signed certificates are acceptable for the testing environment
8. There are no specific performance requirements for the compliance testing