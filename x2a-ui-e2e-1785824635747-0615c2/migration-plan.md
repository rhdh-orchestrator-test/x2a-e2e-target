# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be retained) and medium complexity for converting the InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML template used in the website deployment. Migration consideration: Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Convert InSpec tests to equivalent Ansible assert tasks
  - Option 3: Maintain InSpec as a standalone tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and control
  - Ansible Content Collections for role management
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration preserves the security hardening that disables SSLv3 and enables only TLSv1.2.
  
- **SSH Hardening**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible testing framework.

- **Vault/secrets management**: 
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework will require mapping InSpec resources to equivalent Ansible modules or Testinfra methods.
  - Mitigation: Create a mapping document for InSpec resources to Ansible/Testinfra equivalents.

- **Deployment Script Conversion**: The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Break down the scripts into discrete tasks and map each to equivalent Ansible modules.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, can be retained with minimal changes
2. **Testing Framework**: Convert InSpec tests to Ansible Molecule with Testinfra
3. **Deployment Scripts**: Convert Chef deployment scripts to Ansible playbooks

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.
2. The InSpec tests are used to validate the Ansible playbook configurations rather than as part of a larger compliance framework.
3. The deployment scripts are examples and not used in production environments, given the hardcoded credentials.
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
5. The migration will maintain the same functionality but using Ansible-native tools where possible.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.