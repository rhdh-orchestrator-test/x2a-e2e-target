# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while standardizing their structure
3. Maintaining the Chef InSpec testing capabilities within the Ansible framework

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers), given the limited scope and complexity.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
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
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible using the ansible_inspec module or ansible-test framework
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt Test Kitchen to work with pure Ansible
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for Chef server deployment or migrate completely away from Chef infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. This security check should be preserved in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - Self-signed SSL certificates generated in the Ansible playbook
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring Chef InSpec tests continue to work with pure Ansible deployments
  - Mitigation: Use the ansible_inspec module or integrate with ansible-test
  
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same setup steps or consider if Chef infrastructure is still needed

- **Test Kitchen Replacement**: Finding an equivalent testing framework for Ansible
  - Mitigation: Migrate to Ansible Molecule for testing or adapt Test Kitchen configuration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Standardize structure and variable naming
   - Implement Ansible best practices (roles, collections)
   
2. **InSpec Tests**: Moderate complexity
   - Integrate InSpec tests with Ansible testing framework
   - Ensure compliance checks continue to function
   
3. **Chef Deployment Scripts**: High complexity
   - Convert bash scripts to Ansible roles
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The Chef InSpec testing is a critical component that must be preserved
3. The end goal is to have a pure Ansible solution, potentially eliminating the need for Chef components
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The Test Kitchen setup is used for development/testing rather than CI/CD pipelines