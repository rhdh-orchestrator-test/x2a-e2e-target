# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with Chef InSpec for compliance testing and Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests for compliance verification
2. Chef Automate/Chef Infra Server deployment scripts

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The primary work involves converting InSpec tests to Ansible-compatible testing frameworks and updating deployment scripts to use Ansible roles instead of bash scripts.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be preserved with minor updates to align with current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security fixes. Can be preserved with minor updates.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security. Should be converted to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be converted to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Should be converted to Ansible role.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Server deployment. Should be converted to Ansible role.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic compliance checks
  - Option 2: Molecule with Testinfra for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke from Ansible

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles:
  - Create roles for system preparation (hostname, sysctl settings)
  - Create roles for package installation and configuration
  - Use Ansible Vault for secure credential management

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. Migration should maintain or enhance these security settings.
  - Migration approach: Preserve the same security configurations in the Ansible roles, consider updating to include TLS 1.3 support.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Maintain compliance checks for SSH configuration using Ansible's assert module or Testinfra.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain
  - Count of credentials detected: 4 (username, password, email, organization name in setup scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing frameworks may require additional expertise.
  - Mitigation: Start with simple assertions and gradually enhance test coverage. Consider maintaining InSpec if the team has existing expertise.

- **Chef Server Deployment**: If the organization still needs Chef Server after migration, the deployment process needs to be maintained.
  - Mitigation: Create a dedicated Ansible role for Chef Server deployment or consider alternative configuration management approaches.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Update `chef-and-ansible/website_https.yml` and `chef-and-ansible/poodle_fix.yml` to follow current Ansible best practices
   - Replace Test Kitchen with Molecule for testing

2. **InSpec Tests** (Medium complexity)
   - Convert `chef-and-ansible/tests/website_https_verify.rb` and `chef-and-ansible/tests/ssh_profile.rb` to Ansible assertions or Testinfra tests

3. **Chef Deployment Scripts** (High complexity, dependencies)
   - Create Ansible roles to replace `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`
   - Implement Ansible Vault for secure credential storage

### Assumptions

1. The organization is fully migrating away from Chef to Ansible, including for compliance testing.
2. The Chef Automate and Chef Infra Server deployment scripts are being migrated to Ansible for consistency, not because Chef infrastructure is being decommissioned.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The security requirements (TLS 1.2, SSH hardening) will remain the same or become more stringent.
5. Test Kitchen can be replaced with Molecule without loss of testing capabilities.
6. The team has or will acquire expertise in Ansible testing frameworks to replace InSpec knowledge.