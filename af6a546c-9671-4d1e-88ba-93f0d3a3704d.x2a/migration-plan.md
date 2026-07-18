# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec (tests) and Ansible (playbooks)
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Should be migrated to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be converted to an Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - **Option 1**: Use Ansible's built-in `assert` module for basic testing
  - **Option 2**: Use Molecule for more comprehensive testing
  - **Option 3**: Use pytest-ansible for Python-based testing
  - **Option 4**: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for CI/CD pipelines
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.
  - Migration approach: Preserve the existing Ansible tasks in `poodle_fix.yml` and `website_https.yml`

- **SSH Security**: The InSpec test `ssh_profile.rb` checks for secure SSH configuration (disabling root login).
  - Migration approach: Convert to Ansible assert tasks or maintain as a separate compliance check

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Self-signed certificates generated in `website_https.yml`
  - Migration approach: Use Ansible Vault for storing credentials and certificate information

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible assertions

- **Chef Server Replacement**: Replacing Chef Automate/Infra Server functionality with Ansible equivalents.
  - Mitigation: Document the feature mapping between Chef Automate and Ansible AWX/Tower

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Tests** (Medium complexity)
   - `website_https_verify.rb`
   - `ssh_profile.rb`

3. **Chef Server Deployment Scripts** (High complexity)
   - `deploy-chef-server.sh`
   - `deploy-automate.sh`

### Assumptions

1. The primary goal is to move all functionality to Ansible, eliminating dependencies on Chef products.
2. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are working correctly and can be preserved.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality.
5. The repository is primarily for demonstration purposes rather than production use, based on the README description.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
7. The self-signed certificates in the website deployment are for testing purposes and would be replaced with proper certificates in production.