# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with Chef InSpec tests and Chef server deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible playbooks with Chef InSpec tests
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Can be preserved as-is in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs migration to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs migration to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible's built-in `assert` module for simple tests
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should preserve the security hardening that disables SSLv3 and enables only TLSv1.2.
  - Migration approach: Preserve the existing Ansible tasks that configure SSL

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbooks and should be handled securely

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible's assert module for simple tests, and Molecule for more complex scenarios.

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate/Infra Server functionality.
  - Mitigation: Evaluate Ansible AWX/Tower as a replacement for the web UI and job scheduling features.

### Migration Order

1. **InSpec Tests** (Low risk, high value)
   - Convert InSpec tests to Ansible assert tasks or Molecule tests
   - Update testing framework configuration

2. **Chef Server Deployment Scripts** (Moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential handling with Ansible Vault

3. **Test Kitchen Configuration** (Low complexity)
   - Replace Test Kitchen with Molecule for testing Ansible playbooks

### Assumptions

1. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are functioning correctly and do not need significant modifications.
2. The primary goal is to eliminate Chef dependencies while preserving the functionality and security posture.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment scripts are currently used for setting up development/test environments rather than production systems.
5. There are no external dependencies on Chef-specific features that would require additional migration work.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.