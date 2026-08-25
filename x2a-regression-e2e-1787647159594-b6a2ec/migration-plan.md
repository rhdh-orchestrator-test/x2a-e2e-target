# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests while integrating them into an Ansible-native workflow

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains shell scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test for SSH security compliance checking

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec tests but integrate with Ansible using the `ansible_inspec` module or the community.general.inspec module
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt kitchen.yml to work with Ansible-only testing
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles that accomplish the same server setup

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL configuration for Apache. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Hardening**: The InSpec tests check for SSH security compliance.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls tested by InSpec.

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password variables)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the Ansible-only workflow.
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests as part of playbook execution.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced.
  - Mitigation: Consider if full Chef Automate functionality is needed or if simpler Ansible-based alternatives (AWX/Tower) can be used.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already Ansible, just need organization into proper roles
2. **InSpec Tests** (chef-and-ansible/tests/*.rb): Moderate complexity to integrate with Ansible-native testing
3. **Chef Deployment Scripts** (setup-automate/*.sh): Higher complexity, requires creating equivalent Ansible roles

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README.md content.
2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced entirely with Ansible equivalents.
3. The existing Ansible playbooks are functional and should be preserved with minimal changes.
4. The InSpec tests are valuable and should be maintained as part of the Ansible workflow.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure alternatives.
6. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.