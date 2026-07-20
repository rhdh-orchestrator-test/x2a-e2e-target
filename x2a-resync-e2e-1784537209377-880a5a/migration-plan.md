# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components:

1. A Chef InSpec testing framework used with Ansible playbooks
2. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating everything into pure Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for deploying and testing a secure HTTPS website
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Migration consideration: Keep as-is but update to use Ansible collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Keep as-is but update to use Ansible collections.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Migration consideration: Convert to Ansible-native testing with Molecule.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible-native testing with Molecule.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Migration consideration: Convert to Ansible role for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Server deployment. Migration consideration: Convert to Ansible role for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for infrastructure testing
  - Option 2: Use pytest-ansible for more complex test scenarios
  - Option 3: Integrate with other compliance tools like OSCAP

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Compliance scanning tools like OpenSCAP or Ansible's built-in compliance capabilities

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migration.
  - Migration approach: Maintain the same SSL security configurations in the Ansible roles

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening with equivalent tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates generated in playbooks
  - Migration approach: Replace with Ansible Vault for secrets management

### Technical Challenges

- **Compliance Testing**: The repository uses Chef InSpec for compliance testing, which needs to be replaced with Ansible-native solutions.
  - Mitigation strategy: Evaluate Ansible Molecule, pytest-ansible, or integration with compliance tools like OpenSCAP

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem.
  - Mitigation strategy: Implement Ansible AWX/Tower with appropriate compliance plugins

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible): Update `website_https.yml` and `poodle_fix.yml` to use current Ansible best practices and collections
2. **Testing Framework** (Moderate complexity): Convert InSpec tests to Ansible Molecule tests
3. **Chef Deployment Scripts** (High complexity): Create Ansible roles to replace the Chef Automate and Chef Server deployment scripts

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, not for production use
2. The hardcoded credentials in the setup scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There are no external dependencies or integrations beyond what's visible in the repository
5. The migration will preserve all security hardening features present in the original code
6. The Chef InSpec tests are the primary value to preserve, as they define the compliance requirements