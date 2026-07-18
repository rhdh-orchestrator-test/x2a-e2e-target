# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. A Chef InSpec testing framework used alongside Ansible playbooks
2. Ansible playbooks for configuring HTTPS websites and SSL security
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on:
- Replacing Chef InSpec tests with Ansible-compatible testing frameworks (like Molecule)
- Preserving the existing Ansible playbooks with minimal changes
- Converting Chef server deployment scripts to Ansible playbooks

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef server installation, user creation, organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Migration consideration: Can be preserved with minimal changes.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Can be preserved with minimal changes.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Migration consideration: Convert to Ansible Molecule tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule tests.
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook or remove if not needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Ansible's assert module for basic compliance checks
  - Option 3: Integration with other compliance tools like OVAL or OpenSCAP

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Determine if these components are still needed:
  - If yes: Create Ansible playbooks to deploy equivalent functionality
  - If no: Remove these components entirely

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for web servers and fix POODLE vulnerability
  - Migration approach: Preserve existing Ansible tasks but update to current best practices
  - Consider using Ansible Vault for certificate management

- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert to Ansible-native checks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible Molecule which supports similar testing patterns
  - Complexity: Medium

- **Chef Server Deployment**: Replacing Chef server deployment scripts
  - Mitigation: Determine if Chef server is still needed; if not, eliminate this component
  - If needed, create equivalent Ansible playbooks for deployment
  - Complexity: High

### Migration Order

1. **Ansible Playbooks** (Low risk, high value)
   - `website_https.yml` and `poodle_fix.yml` can be preserved with minimal changes
   - Update to current Ansible best practices

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible Molecule
   - Update test configurations

3. **Chef Server Deployment** (High complexity)
   - Determine if Chef server is still needed
   - If needed, create Ansible playbooks to replace deployment scripts

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef server deployment scripts may not be needed in the final Ansible solution
3. The target environment will continue to be Ubuntu 20.04 or similar
4. The hardcoded credentials in the scripts are for demonstration purposes and will be replaced with secure alternatives
5. The existing Ansible playbooks are functional and follow reasonable practices
6. The team has expertise in both Chef and Ansible to facilitate the migration
7. No external dependencies or integrations beyond what's visible in the repository