# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and InSpec tests for web server configuration and testing
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache2 installation, SSL configuration, HTTPS setup, security testing

- **chef-and-ansible/tests**:
    - Description: Directory containing Chef InSpec tests for verifying HTTPS functionality and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification, SSH security compliance

- **setup-automate**:
    - Description: Directory containing Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server
- `chef-and-ansible/website_https.yml`: Ansible playbook for setting up HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configurations
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with `ansible-test` for integration testing
  - Use Molecule for Ansible role testing
  - Consider Ansible Lint for static code analysis
  - For compliance testing similar to InSpec, consider migrating to:
    - OpenSCAP with Ansible
    - Ansible's `assert` module for basic tests
    - Python's pytest for more complex testing scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in inventory management for multi-node testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable older protocols
  - Ensure proper certificate generation and management

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be preserved
  - Convert the STIG compliance checks to Ansible assertions or OpenSCAP
  - Maintain the security tags and compliance metadata

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (deploy-automate.sh, deploy-chef-server.sh)
    - Replace with Ansible Vault for secure credential storage
  - Self-signed certificates generated in website_https.yml
    - Use Ansible's crypto modules for certificate management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing style to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's expectations
  - Consider using Python-based testing frameworks for more complex assertions

- **Compliance Metadata**: Preserving compliance metadata (CCI IDs, STIG IDs, etc.) from InSpec tests
  - Mitigation: Document compliance mappings in Ansible playbook comments or separate documentation
  - Consider using Ansible tags to maintain traceability to compliance requirements

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible equivalents
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower

### Migration Order

1. **InSpec Tests** (low risk, high value) - Convert to Ansible assertions or Molecule tests
   - chef-and-ansible/tests/website_https_verify.rb
   - chef-and-ansible/tests/ssh_profile.rb
2. **Ansible Playbooks** (already Ansible, minimal changes needed)
   - chef-and-ansible/website_https.yml
   - chef-and-ansible/poodle_fix.yml
3. **Chef Deployment Scripts** (moderate complexity) - Convert to Ansible roles or replace with AWX/Tower deployment
   - setup-automate/deploy-automate.sh
   - setup-automate/deploy-chef-server.sh

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The target environment will continue to be Ubuntu 20.04 as specified in the kitchen.yml
3. The deployment scripts for Chef Automate and Chef Server may not be needed if the migration is fully to Ansible
4. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests must be preserved in the Ansible implementation
5. Test Kitchen is used primarily for development and testing, not for production deployments
6. The self-signed certificates are for testing purposes and may need to be replaced with proper certificate management in production
7. The repository does not contain actual Chef cookbooks, only InSpec tests and Ansible playbooks
8. The migration will maintain the same level of security hardening present in the original code