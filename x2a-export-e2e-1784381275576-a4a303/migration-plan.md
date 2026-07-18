# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks with Chef InSpec for compliance testing. The migration scope involves consolidating all infrastructure management into Ansible while preserving or enhancing the compliance testing capabilities. The repository has two main components:

1. Chef Automate and Chef Infra Server deployment scripts (Bash)
2. Ansible playbooks with Chef InSpec tests for configuring and validating HTTPS websites

The migration complexity is moderate, with most effort focused on replacing the Chef server deployment scripts with equivalent Ansible roles. The estimated timeline for this migration is 2-3 weeks, with the following breakdown:
- Week 1: Develop Ansible roles to replace Chef deployment scripts
- Week 2: Refactor existing Ansible playbooks into proper roles with improved structure
- Week 3: Implement testing framework and finalize documentation

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration consideration: Refactor into an Ansible role with proper variables and documentation.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Integrate into a comprehensive Apache security role.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Keep as compliance test or convert to Ansible assert tasks.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration consideration: Keep as compliance test or convert to Ansible assert tasks.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Create an Ansible role for infrastructure management platform deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Create an Ansible role for Chef Server deployment if still needed, or replace with Ansible AWX/Tower.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management or consider if Chef Automate is still needed in the target environment
- **Chef InSpec**: Retain as a compliance testing tool alongside Ansible, leveraging its specialized compliance capabilities
- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Apache 2.4.41**: Ensure compatibility with target environment and implement as an Ansible role
- **OpenSSL**: Implement proper certificate management using Ansible's crypto modules

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved and enhanced in the migrated Ansible roles.
- **SSH Security**: The InSpec profile checks for secure SSH configuration (disabling root login). This should be implemented as an Ansible role for SSH hardening.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username: 'jtonello', password: 'password') should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain
  - Consider implementing a more robust secret management solution for production environments

### Technical Challenges

- **Chef Automate Replacement**: Determining if Chef Automate functionality is still required or if it can be replaced entirely with Ansible Tower/AWX or another solution
- **Compliance Testing Strategy**: Deciding whether to keep InSpec for compliance testing or migrate to native Ansible testing capabilities
- **Testing Framework**: Migrating from Test Kitchen to Ansible Molecule for testing infrastructure
- **Apache Configuration**: Ensuring the Apache configuration is properly parameterized and follows Ansible best practices

### Migration Order

1. **Apache HTTPS Configuration** (Low risk, already in Ansible format)
   - Refactor `website_https.yml` into a proper Ansible role with variables
   - Integrate `poodle_fix.yml` into the Apache security configuration
   - Update testing framework from Test Kitchen to Molecule

2. **Chef Deployment Scripts** (Moderate complexity)
   - Create Ansible roles to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement proper secret management with Ansible Vault
   - Add proper error handling and idempotency

3. **Compliance Testing** (Low complexity)
   - Decide on compliance testing strategy (keep InSpec or migrate to Ansible)
   - Implement chosen strategy with proper integration into CI/CD pipeline

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The Chef deployment scripts are used for setting up a Chef environment that would run InSpec for compliance testing.
3. The target environment will continue to need compliance testing capabilities.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
5. The Apache configuration is a sample application and not a production website.
6. The migration will consolidate all functionality into Ansible while potentially keeping InSpec for compliance testing if needed.
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
8. The organization requires both infrastructure automation and compliance validation capabilities.