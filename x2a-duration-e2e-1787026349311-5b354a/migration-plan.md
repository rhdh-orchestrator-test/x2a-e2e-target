# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining the InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible's built-in assertion modules
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with the `kitchen-ansible` plugin
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and remediate POODLE vulnerability. Migration must maintain these security controls.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls tested by InSpec

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Maintaining InSpec tests while moving to an Ansible-only workflow
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests from Ansible playbooks

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Map Chef Server functions to Ansible Automation Platform or AWX features

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Standardize variable naming and structure
   - Add documentation
   - Convert to roles for better organization

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Use Ansible Vault for credentials

3. **Testing Framework**: Medium complexity
   - Migrate Test Kitchen configuration to Ansible Molecule
   - Maintain InSpec tests but run them through Ansible

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README description
2. The Chef Automate and Chef Infra Server deployment scripts are intended for on-premises or generic cloud VM deployment
3. The InSpec tests are meant to be run against systems configured by the Ansible playbooks
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The repository does not contain complete Chef cookbooks, only deployment scripts for Chef infrastructure
6. The existing Ansible playbooks are already functional and only need standardization
7. The target audience is users looking to use Chef InSpec with Ansible for compliance automation