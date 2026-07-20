# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting these components to pure Ansible solutions.

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Mixed (Chef InSpec tests + Ansible playbooks)
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration will require converting to Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Will need to be converted to Ansible-compatible tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configurations. Will need to be converted to Ansible-compatible tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Will need to be replaced with Ansible playbooks for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need to be replaced with Ansible playbooks for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible Molecule with Testinfra for testing
  - Option 2: Ansible Molecule with Goss for testing
  - Option 3: Maintain InSpec as a standalone tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Collections for configuration management
  - Compliance scanning using OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure these security configurations are preserved during migration.
  - Migration approach: Preserve the existing Ansible tasks for SSL configuration.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assert modules or Molecule/Testinfra tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbooks and should be handled securely
  - Count of credentials detected: 3 (username, password, email in setup scripts)

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec, or maintain InSpec as a standalone tool.

- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server deployment with Ansible Tower/AWX.
  - Mitigation: Create Ansible playbooks that deploy and configure Ansible Tower/AWX with similar functionality.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `chef-and-ansible/website_https.yml`
   - `chef-and-ansible/poodle_fix.yml`

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Ansible Molecule/Testinfra
   - Update test orchestration from Test Kitchen to Molecule

3. **Infrastructure Deployment** (High complexity)
   - Replace Chef Automate/Infra Server deployment scripts with Ansible playbooks for Ansible Tower/AWX

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The Chef components (InSpec, Automate, Infra Server) are being used primarily for compliance testing and reporting, not for configuration management.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the scripts could be adapted for other environments.

4. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with secure credential management in production.

5. The self-signed certificates generated in the playbooks are for testing purposes and would be replaced with proper certificates in production.

6. The migration will focus on preserving the functionality of the existing components while moving to an Ansible-native approach where possible.