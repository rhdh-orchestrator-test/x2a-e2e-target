# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations, with a focus on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and fixing SSL vulnerabilities, along with Chef InSpec tests for verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly used in Ansible with minor updates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly used in Ansible with minor updates.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need conversion to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need conversion to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Will need replacement with Ansible roles.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Will need replacement with Ansible roles.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule for testing infrastructure
  - Option 2: Integrate with pytest-ansible for more advanced testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-native management platforms

### Security Considerations

- **SSL Configuration**: The repository includes specific SSL hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security configurations are maintained in the migrated Ansible playbooks.
  - Migration approach: Preserve the same SSL configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec profile checks for SSH root login being disabled. Ensure this security check is maintained.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-native testing will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Create a mapping document for InSpec resources to Ansible equivalents and validate each test conversion

- **Chef Server Deployment**: The Chef server deployment scripts will need to be completely replaced with Ansible roles.
  - Mitigation: Create new Ansible roles that achieve the same configuration outcomes as the shell scripts

### Migration Order

1. **Ansible Playbooks** (Low risk, high value)
   - Migrate `website_https.yml` and `poodle_fix.yml` to standardized Ansible roles
   - Update any deprecated syntax or modules

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Ansible Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef Server Deployment** (High complexity)
   - Create Ansible roles to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration and examples, not production use
2. The InSpec tests are considered valuable and should be preserved in functionality
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Vagrant will continue to be used for development/testing environments
5. The hardcoded credentials in the scripts are for demonstration purposes only and will be replaced with secure alternatives
6. The Apache configuration parameters (ports, certificates, etc.) should be preserved in the migration