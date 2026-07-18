# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while enhancing them with best practices
3. Maintaining Chef InSpec tests as they are already compatible with Ansible

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing or maintain as-is since it's already using Ansible as the provisioner.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Migration consideration: Keep as-is but refactor to use Ansible roles and collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for hardening SSL configuration. Migration consideration: Keep as-is but integrate into a comprehensive security role.
- `chef-and-ansible/tests/*.rb`: InSpec test files for verifying website functionality and SSH security. Migration consideration: Keep as-is as InSpec is compatible with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

- **Operating System**: Ubuntu 20.04 (based on kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible playbooks that configure equivalent monitoring/compliance solution
- **Chef Infra Server**: Replace with Ansible AWX/Tower or alternative configuration management approach
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain as-is since it's already using Ansible as the provisioner
- **InSpec**: Keep as-is for compliance testing as it works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and implement security hardening. Maintain these security practices in the migrated solution.
- **SSH Hardening**: InSpec tests verify SSH security configurations. Ensure these tests continue to pass after migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed SSL certificates in website_https.yml
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality (compliance, reporting, visibility). Consider Ansible AWX/Tower with additional tools like Prometheus/Grafana for monitoring.
- **InSpec Integration**: Ensuring continued integration of InSpec tests with the Ansible workflow. This can be addressed by using Ansible's built-in support for InSpec or by integrating InSpec into the CI/CD pipeline.

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, already Ansible): Refactor existing playbooks to use roles and best practices
2. **setup-automate Bash Scripts** (moderate complexity): Convert to Ansible playbooks for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code.
2. The Chef Automate and Chef Infra Server deployments are for demonstration/lab environments, not production.
3. The hardcoded credentials in the setup scripts are not used in production environments.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations not visible in the repository.
6. The InSpec tests should be preserved as-is since they provide valuable compliance checks.