# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a standardized Ansible approach. The repository appears to be primarily a set of examples for demonstration purposes rather than a production infrastructure codebase. The migration scope is relatively small, with two main components:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec tests

The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure web server with SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities (POODLE)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions
  - Migration strategy: Convert InSpec tests to Ansible Molecule with testinfra or use ansible-lint
  - Alternative: Keep InSpec as a testing tool but integrate with Ansible workflow

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - Migration strategy: Replace Chef server deployment with Ansible AWX/Tower deployment

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening that must be preserved
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2) in migrated playbooks
  
- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Use the same Ansible openssl modules in the migrated solution

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Test Kitchen Integration**: The current setup uses Test Kitchen with Ansible and InSpec
  - Mitigation strategy: Replace with Ansible Molecule for testing or maintain Test Kitchen with adjusted configuration

- **Compliance Testing**: InSpec is used for compliance testing
  - Mitigation strategy: Either continue using InSpec with Ansible or migrate to Ansible-native testing tools

### Migration Order

1. **website-https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Convert InSpec tests to Ansible-native testing if desired

2. **Chef Automate/Infra Server deployment scripts** (moderate complexity)
   - Convert Bash scripts to Ansible roles for deploying alternative infrastructure

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems
3. There is no actual Chef cookbook code to migrate, only Chef infrastructure setup scripts
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The security requirements include TLS 1.2 and disabling older protocols
6. The deployment scripts are for on-premises or generic cloud VMs
7. No external dependencies or third-party modules are used beyond standard Ansible modules
8. The migration will maintain the same functionality but standardize on Ansible