# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need to be consolidated into a unified Ansible solution. The repository primarily consists of Chef Automate and Chef Infra Server deployment scripts, along with Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification.

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The main focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks. The estimated timeline for this migration is 1-2 weeks, depending on the complexity of the Chef Automate setup requirements.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include updating the testing framework if needed.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include preserving compliance testing capabilities.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations include maintaining security compliance checks.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible playbooks for infrastructure management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbooks for infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Infra Server**: Replace with Ansible roles for configuration management
- **InSpec**: Maintain InSpec for compliance testing or migrate to Ansible-compatible testing frameworks like Molecule with TestInfra

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening for Apache SSL configuration (disabling SSLv3, enabling TLSv1.2)
- **SSH Security**: Maintain SSH security compliance checks
- **Vault/secrets management**: 
  - 5 hardcoded credentials detected in setup-automate scripts (username, password, email, organization name, hostname)
  - SSL certificate and key files in the Apache configuration
  - Replace hardcoded credentials with Ansible Vault or other secure credential management

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate's functionality, which may require multiple Ansible roles and external tools
- **Compliance Testing**: Ensuring that the compliance testing capabilities provided by InSpec are maintained in the Ansible ecosystem
- **Infrastructure Deployment**: Creating Ansible playbooks that can deploy and configure the infrastructure management tools that will replace Chef Automate and Chef Infra Server

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **InSpec Tests** (Moderate complexity)
   - Determine whether to keep InSpec or migrate to an Ansible-compatible testing framework
   - If keeping InSpec, ensure it works with the new Ansible-only workflow

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible roles and playbooks to replace Chef Automate and Chef Infra Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the chef-and-ansible/README.md.
2. The Chef deployment scripts are used for setting up the infrastructure that would run the Ansible playbooks and InSpec tests.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.
4. The security compliance requirements, particularly around SSL/TLS and SSH configurations, must be maintained in the migrated solution.
5. The current setup uses hardcoded credentials which should be replaced with a more secure approach in the migration.
6. The InSpec tests are valuable for compliance verification and should either be maintained or replaced with equivalent functionality.