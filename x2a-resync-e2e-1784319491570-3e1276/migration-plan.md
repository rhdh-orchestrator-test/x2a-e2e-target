# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec tests for compliance automation
3. Test Kitchen configuration for infrastructure testing

The migration complexity is relatively low as most of the Ansible components are already in place. The main focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-native workflow.

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal disruption to existing operations.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec integration for compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Can be kept as-is or refactored to use Ansible roles.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be kept as-is or integrated into the main website deployment playbook.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment. Should be migrated to Ansible-native testing or kept as InSpec tests run by Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be migrated to Ansible-native testing or kept as InSpec tests run by Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Should be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be replaced with Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Replace with Ansible-native testing using assert modules and custom modules
  2. Keep InSpec and call it from Ansible using the `command` or `shell` module
  3. Use Ansible's built-in `inspec` module to continue using InSpec tests

- **Test Kitchen**: Currently used for testing infrastructure. Replace with Molecule for Ansible-native testing.

- **Chef Automate/Infra Server**: Currently deployed via bash scripts. Replace with:
  1. Ansible playbooks for deploying alternative compliance and infrastructure management tools
  2. If Chef Automate functionality is still required, create Ansible playbooks that deploy Chef Automate using the official installation methods

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for web servers. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Keep the existing OpenSSL tasks in the Ansible playbooks, but consider using Ansible Vault for storing sensitive information.

- **SSH Security**: InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible migration.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or keep using InSpec for verification.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, which is acceptable for testing but should use proper certificate management for production

### Technical Challenges

- **InSpec Integration**: Ensuring that compliance testing remains robust when migrating from Chef InSpec to Ansible-native testing or maintaining InSpec within Ansible.
  - Mitigation: Use Ansible's `inspec` module or maintain separate InSpec tests that can be called from Ansible.

- **Test Kitchen Replacement**: Ensuring that infrastructure testing remains effective when migrating from Test Kitchen to Molecule.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen configuration.

- **Chef Automate Functionality**: If Chef Automate functionality is still required, ensuring it can be properly deployed and configured via Ansible.
  - Mitigation: Create detailed Ansible playbooks that follow Chef's official installation documentation.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Refactor existing Ansible playbooks to use roles and best practices
2. **Testing Framework** (Moderate complexity): Migrate from Test Kitchen to Molecule
3. **Chef Deployment Scripts** (High complexity): Replace bash scripts with Ansible playbooks for deploying alternative tools or Chef itself

### Assumptions

1. The primary goal is to move to a pure Ansible solution, potentially eliminating Chef components entirely.
2. InSpec testing can either be replaced with Ansible-native testing or maintained as a separate tool called from Ansible.
3. The current setup is used for demonstration/educational purposes (based on the repository description) rather than production, so some simplifications may be acceptable.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The Vagrant/VM infrastructure will be maintained, but the scripts should be adaptable to cloud environments.