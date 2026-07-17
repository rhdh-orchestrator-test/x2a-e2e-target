# MIGRATION FROM CHEF INSPEC AND BASH TO ANSIBLE

## Executive Summary

This repository contains Chef InSpec tests integrated with Ansible playbooks for compliance automation, along with bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is focused on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving existing Ansible playbooks, and converting Chef deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment with Ansible, SSL/TLS compliance testing with InSpec, SSH security testing with InSpec

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec - needs to be migrated to Ansible Molecule or another Ansible-native testing framework
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website - can be preserved as-is
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities - can be preserved as-is
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website - needs to be converted to Ansible-compatible test
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance - needs to be converted to Ansible-compatible test
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate - needs to be converted to Ansible playbook
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server - needs to be converted to Ansible playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for compliance testing
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for automation platform
  - Ansible Content Collections for configuration management

### Security Considerations

- **SSL/TLS Configuration**: The repository contains specific SSL/TLS hardening configurations:
  - Migration must preserve TLS 1.2 requirement and disable SSL3
  - Self-signed certificates generation must be maintained
  - Consider updating to include TLS 1.3 support

- **SSH Security**: The repository includes SSH hardening tests:
  - Root login restrictions must be maintained
  - Consider expanding SSH hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate handling should use Ansible Vault for private keys
  - Count of credentials detected:
    - setup-automate scripts: 3 hardcoded credentials (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks while maintaining the same level of compliance validation
  - Mitigation: Use Ansible assert modules or integrate with testinfra/Goss for similar functionality

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting with Ansible-native solutions
  - Mitigation: Consider integrating with tools like Compliance as Code (CaC) frameworks or OpenSCAP

- **Test Kitchen to Molecule**: Converting the test workflow from Test Kitchen to Molecule
  - Mitigation: Molecule provides similar functionality but with an Ansible-native approach

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Preserve existing playbooks (website_https.yml, poodle_fix.yml)
2. **InSpec Tests** (Moderate complexity): Convert InSpec tests to Ansible-compatible testing framework
   - website_https_verify.rb: Convert to Ansible Molecule tests
   - ssh_profile.rb: Convert to Ansible Molecule tests
3. **Test Kitchen Configuration** (Moderate complexity): Replace kitchen.yml with Ansible Molecule configuration
4. **Chef Deployment Scripts** (High complexity): Convert to Ansible playbooks for deploying alternative solutions
   - deploy-automate.sh: Convert to Ansible playbook for AWX/Tower deployment
   - deploy-chef-server.sh: Convert to Ansible playbook for configuration management

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't need modification
3. The team is familiar with Ansible but may need training on Ansible testing frameworks
4. The deployment environment will remain similar (Ubuntu 20.04 on Vagrant VMs)
5. There's no requirement to maintain backward compatibility with Chef InSpec
6. The Chef Automate and Chef Infra Server deployment scripts are used for demonstration purposes and not production environments
7. The hardcoded credentials in the deployment scripts are not used in production environments
8. The self-signed certificates are acceptable for the testing environment