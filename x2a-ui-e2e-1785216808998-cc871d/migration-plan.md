# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and migrating Chef server deployment scripts to Ansible roles. The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen-ansible)**: Replace with Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing but integrate with Ansible Molecule
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX/Tower

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **POODLE Vulnerability Mitigation**: The poodle_fix.yml playbook addresses the POODLE vulnerability by enforcing TLSv1.2. This security hardening must be preserved.
- **SSH Hardening**: The SSH InSpec profile checks for root login restrictions. This compliance check should be maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in Chef deployment scripts (username, password)
  - Self-signed SSL certificates generated during deployment
  - Recommend implementing Ansible Vault for credential storage

### Technical Challenges

- **InSpec Integration**: Maintaining InSpec tests while migrating to a pure Ansible workflow may require additional configuration.
- **Chef Server Migration**: Replacing Chef Server deployment with Ansible requires careful planning for configuration management workflow changes.
- **Compliance Automation**: Ensuring that compliance checks remain effective after migration.

### Migration Order

1. **website-https playbook** (low risk, already Ansible)
   - Refactor into Ansible role structure
   - Implement variable files instead of inline variables
   - Maintain InSpec tests

2. **poodle-fix playbook** (low risk, already Ansible)
   - Refactor into Ansible role structure
   - Consider merging with website-https role as a security enhancement

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement Ansible Vault for credential storage
   - Consider alternatives like Ansible Automation Platform

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef deployment scripts are used for setting up Chef infrastructure, not for actual configuration management of applications.
3. InSpec is being used alongside Ansible for compliance testing, and this integration should be maintained.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.
5. No external dependencies or complex infrastructure are involved beyond what's explicitly defined in the repository.