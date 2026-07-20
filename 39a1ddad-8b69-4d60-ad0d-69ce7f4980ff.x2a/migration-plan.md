# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef server and Automate deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL configuration testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Migration consideration: Keep as-is, but update testing framework.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Keep as-is, but update testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook or remove if not needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for infrastructure testing
  - Option 3: Maintain InSpec as a standalone tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the same SSL parameters in the Ansible tasks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec test to equivalent Ansible assert or Molecule test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks.
  - Mitigation: Use Molecule with Testinfra or Goss, which provide similar functionality to InSpec
  
- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible.
  - Mitigation: Create Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower deployment

### Migration Order

1. **Ansible Playbooks** (Low risk): Keep existing playbooks (website_https.yml, poodle_fix.yml) as they are already in Ansible format
2. **Testing Framework** (Moderate complexity): Convert InSpec tests to Molecule with Testinfra or Goss
3. **Deployment Scripts** (High complexity): Convert Chef deployment scripts to Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The Chef server deployment scripts may not be needed if the migration is fully to Ansible.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure credential management in production.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the playbooks should be adaptable to other environments.
5. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and only need testing framework updates.
6. There are no external dependencies or complex integrations beyond what is visible in the repository.