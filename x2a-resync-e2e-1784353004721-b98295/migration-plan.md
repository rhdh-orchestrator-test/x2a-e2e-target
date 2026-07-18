# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks for a single engineer, as the codebase is small and well-structured. The main challenge will be replacing Chef InSpec testing with equivalent Ansible testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly reused in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Can be directly reused in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Needs conversion to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider OpenSCAP integration for compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for configuration management
  - CI/CD pipeline integration for automated testing and deployment

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in `poodle_fix.yml`
  - Approach: Preserve the existing Ansible task that enforces TLSv1.2
  
- **SSH Hardening**: The InSpec profile in `ssh_profile.rb` checks for secure SSH configuration
  - Approach: Convert InSpec tests to Ansible assertions or include the `devsec.hardening.ssh_hardening` role

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
    - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Testing Framework Transition**: Moving from Chef InSpec to Ansible-native testing
  - Mitigation: Create equivalent tests using Ansible's assert module or Molecule
  - Consider using community collections like `community.general.assert_equal` for more complex assertions

- **Chef Server Replacement**: Determining the appropriate Ansible infrastructure to replace Chef Server functionality
  - Mitigation: Document clear workflows for how teams will transition from Chef Server to Ansible AWX/Tower or other solutions

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk, already in Ansible format
   - Consolidate existing Ansible playbooks into a structured Ansible project
   - Update any deprecated syntax or modules

2. **Testing Framework** (chef-and-ansible/tests/*.rb): Medium complexity
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure equivalent coverage for security and functionality tests

3. **Chef Deployment Scripts** (setup-automate/*.sh): High complexity
   - Convert bash scripts to Ansible playbooks for deploying alternative infrastructure
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use (based on README.md content)
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which will be replaced by an Ansible-based solution
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in the migration
7. The organization using this repository is transitioning from a mixed Chef/Ansible environment to a pure Ansible solution