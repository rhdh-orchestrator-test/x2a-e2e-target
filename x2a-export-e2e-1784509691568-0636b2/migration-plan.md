# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of a web server
    - Path: chef-and-ansible
    - Technology: Chef InSpec (for testing) and Ansible (for configuration)
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Can be preserved as-is in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for lightweight testing
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab/GitHub for version control
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the same security settings are maintained in the migrated solution.
  - Migration approach: Preserve the existing Ansible tasks for SSL configuration.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec test to equivalent Ansible assert or Molecule verification.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing pre-generated certificates or keys

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec, or maintain InSpec as a standalone tool.

- **Chef Server Deployment**: Replacing Chef Automate/Infra Server deployment with equivalent Ansible management.
  - Mitigation: Deploy AWX/Tower using Ansible playbooks, which provides similar functionality to Chef Automate.

### Migration Order

1. **Ansible Playbooks** (Low risk, no changes needed)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Molecule/Testinfra
   - Replace Test Kitchen with Molecule

3. **Chef Server Deployment Scripts** (High complexity)
   - Convert Chef Automate/Infra Server deployment scripts to Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The Chef InSpec tests are used for compliance verification only, not for configuration management.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with secure alternatives in production.
5. The self-signed certificates generated in the playbooks are for testing purposes only and would be replaced with proper certificates in production.
6. The migration will focus on preserving the functionality of the existing solution while moving away from Chef-specific components.