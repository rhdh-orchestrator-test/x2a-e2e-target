# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example showing Chef InSpec tests with Ansible playbooks for HTTPS website deployment and SSL configuration
    - Path: chef-and-ansible
    - Technology: Ansible playbooks with Chef InSpec tests
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Migration consideration: Can be kept as-is in the Ansible repository.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL configuration. Migration consideration: Can be kept as-is in the Ansible repository.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website. Migration consideration: Convert to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH configuration compliance. Migration consideration: Convert to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - **Option 1**: Use Ansible's built-in `assert` module for basic testing
  - **Option 2**: Use Molecule with Testinfra for more comprehensive testing
  - **Option 3**: Use Ansible Lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the existing SSL configuration in the Ansible playbooks.

- **SSH Security**: The InSpec tests check for SSH root login being disabled.
  - Migration approach: Convert the InSpec test to an equivalent Ansible assertion or Testinfra test.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Map InSpec resources to equivalent Testinfra or Ansible assert statements. For example, convert `describe port(443)` to Testinfra's `host.socket("tcp://0.0.0.0:443").is_listening`.

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef server deployment, using the official Chef installation documentation as a reference.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Replace Test Kitchen with Molecule

3. **Chef Server Deployment Scripts** (Medium complexity)
   - Convert Bash scripts to Ansible playbooks

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing.
2. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are functioning correctly and don't need significant changes.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment scripts for Chef Automate and Chef Infra Server will be converted to equivalent Ansible playbooks that deploy the same software.
5. No additional Chef cookbooks or resources are present in the repository beyond what was discovered.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.