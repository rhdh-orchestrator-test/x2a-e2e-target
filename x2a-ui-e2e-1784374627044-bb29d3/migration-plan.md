# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring web servers with SSL
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache web server configuration, SSL setup, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like:
  - Ansible Molecule for infrastructure testing
  - ansible-lint for playbook linting
  - Consider keeping InSpec as a compliance tool if already integrated into workflows

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Vagrant directly if VM-based testing is still required

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform (AWX/Tower) for enterprise automation
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP or maintained InSpec tests

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain:
  - Self-signed certificate generation
  - TLS 1.2 enforcement (POODLE vulnerability fix)
  - Proper file permissions for certificates

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement
  - Ensure Ansible playbooks maintain this security practice
  - Consider expanding SSH hardening with Ansible security roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in setup-automate scripts

### Technical Challenges

- **Compliance Testing**: Maintaining compliance testing capabilities
  - Solution: Either integrate InSpec with Ansible or migrate to Ansible-native testing tools
  - Consider using ansible-test or Molecule for functional testing and OpenSCAP for compliance

- **Certificate Management**: Ensuring proper certificate generation and management
  - Solution: Use Ansible's crypto modules (openssl_*) which are already in use in the existing playbooks

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` to Ansible roles for better organization
   - Update any deprecated Ansible syntax

2. **Testing Framework** (Moderate complexity)
   - Replace Test Kitchen with Ansible Molecule
   - Decide whether to keep InSpec or migrate to Ansible-native testing

3. **Chef Automate/Server Deployment** (High complexity)
   - Create Ansible playbooks to replace the bash scripts for infrastructure setup
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The Chef InSpec tests are used for compliance verification of infrastructure configured by Ansible, suggesting a hybrid approach that could be maintained or fully migrated to Ansible.

3. The setup scripts for Chef Automate and Chef Infra Server are used for setting up a Chef environment, which would be replaced by an Ansible Automation Platform in the migrated solution.

4. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with proper secret management in production.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

6. There are no complex Chef cookbooks or recipes to migrate, as the repository focuses on Ansible playbooks with Chef InSpec testing and Chef server setup scripts.