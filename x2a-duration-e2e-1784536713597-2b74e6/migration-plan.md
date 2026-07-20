# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with clear purposes.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec tests. Migration will require converting to Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security. Needs to be converted to an Ansible-compatible test.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs to be converted to an Ansible-compatible test.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks:
  - Option 1: Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for infrastructure testing
  - Option 3: Ansible Lint for static analysis and best practices

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Content Collections for configuration management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS configurations and tests:
  - Ensure TLS 1.2 is enabled and SSL3 is disabled
  - Self-signed certificate generation
  - These configurations should be preserved in the Ansible migration

- **SSH Security**: The repository includes SSH security tests:
  - Disabling root login via SSH
  - These tests should be converted to Ansible-compatible tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance validation.
  - Mitigation: Use Ansible Molecule with testinfra or Goss plugins to achieve similar testing capabilities.

- **Test Kitchen to Molecule**: Converting Test Kitchen workflow to Ansible Molecule.
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration.

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem.
  - Mitigation: Implement Ansible Tower/AWX with appropriate collections and roles.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Preserve existing playbooks (website_https.yml, poodle_fix.yml)
2. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible-compatible testing framework
3. **Test Kitchen Configuration** (Medium complexity): Convert to Ansible Molecule
4. **Chef Deployment Scripts** (High complexity): Convert to Ansible playbooks for deploying Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec with Ansible, as indicated in the README.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and can be preserved as-is.
3. The Chef InSpec tests are used for compliance validation and need to be converted to an Ansible-compatible testing framework.
4. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which will be replaced with Ansible Tower/AWX.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with Ansible Vault in the migration.
7. No external dependencies or integrations beyond what's visible in the repository are required for the migration.