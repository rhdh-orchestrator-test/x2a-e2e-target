# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing for compliance automation
3. Test Kitchen configuration for infrastructure testing

The migration complexity is relatively low as most of the Ansible components are already in place and functioning. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks. The estimated timeline for this migration is 1-2 weeks, depending on the complexity of the Chef Automate functionality that needs to be replicated.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache web server deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Migration consideration: Can be kept as-is or refactored into Ansible roles.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Can be kept as-is or integrated into a security role.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Convert to Ansible assert tasks or keep InSpec for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration consideration: Convert to Ansible assert tasks or keep InSpec for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration consideration: Replace with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Keep InSpec for compliance testing and integrate with Ansible
  2. Replace with native Ansible assertions and community modules for compliance testing
  3. Consider alternative compliance tools like OpenSCAP with Ansible integration

- **Test Kitchen**: Currently used for testing infrastructure. Replace with Ansible Molecule for testing Ansible roles and playbooks.

- **Chef Automate/Infra Server**: Currently deployed via bash scripts. Replace with:
  1. Ansible AWX/Tower for enterprise automation platform
  2. Ansible playbooks for configuration management
  3. Consider GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: InSpec tests verify SSH security configurations.
  - Migration approach: Create Ansible roles for SSH hardening that implement the same controls tested by InSpec.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: The repository uses Chef InSpec for compliance testing, which is well-integrated with the current workflow.
  - Mitigation strategy: Either maintain InSpec for compliance testing or develop equivalent testing using Ansible's assert module and community modules.

- **Chef Automate Functionality**: The Chef Automate deployment provides enterprise features that need equivalent solutions in the Ansible ecosystem.
  - Mitigation strategy: Evaluate AWX/Tower as a replacement for Chef Automate's UI and workflow capabilities.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Refactor existing Ansible playbooks into roles for better organization
2. **Testing Framework** (Moderate complexity): Replace Test Kitchen with Ansible Molecule
3. **Chef Automate/Infra Server** (High complexity): Replace with Ansible AWX/Tower and appropriate playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.
2. The Chef components (Automate and Infra Server) are used for demonstration purposes and not for production workloads.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The security requirements include SSL configuration and SSH hardening.
5. There are no complex Chef cookbooks or recipes that need migration, only deployment scripts.
6. The InSpec tests are valuable and should be preserved or converted to equivalent Ansible tests.
7. The hardcoded credentials in the scripts are for demonstration purposes and would be replaced with secure credential management in production.