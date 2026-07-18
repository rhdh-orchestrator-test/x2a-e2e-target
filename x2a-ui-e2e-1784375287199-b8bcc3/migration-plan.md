# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need to be consolidated into a pure Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts (in Bash)
2. Ansible playbooks for configuring HTTPS websites with InSpec tests for compliance verification

The migration scope is relatively small, with only a few files to migrate. The estimated timeline for this migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in Ansible format) and medium complexity for the Chef server deployment scripts (need conversion to Ansible).

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, compliance testing with InSpec

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring HTTPS website. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Migration consideration: Convert to Ansible Molecule tests or maintain InSpec tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH configuration. Migration consideration: Convert to Ansible Molecule tests or maintain InSpec tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible role for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible role for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Ansible playbooks targeting Apache 2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Server CLI**: Replace with Ansible roles for infrastructure management
- **InSpec**: Decision needed - either maintain InSpec for compliance testing or migrate to Ansible-native solutions:
  - Option 1: Keep InSpec tests and call them from Ansible using the `inspec` module
  - Option 2: Replace with Ansible assert modules and custom modules for compliance testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Maintain the existing SSL configuration in the Ansible playbooks.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create Ansible tasks to enforce SSH security configurations and verify compliance.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password, email)
  - SSL certificate generation and management
  - Migration approach: Replace hardcoded credentials with Ansible Vault or external secret management solution.

### Technical Challenges

- **Chef Automate Deployment**: The current solution uses bash scripts to deploy Chef Automate and Chef Infra Server.
  - Mitigation strategy: Create Ansible roles to handle the deployment of alternative infrastructure management tools or migrate to cloud-native solutions.

- **Compliance Testing**: The current solution uses InSpec for compliance testing.
  - Mitigation strategy: Either maintain InSpec tests and call them from Ansible, or develop equivalent tests using Ansible's built-in modules.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk, already in Ansible format
2. **InSpec Tests** (chef-and-ansible/tests/): Moderate complexity, need to decide on testing strategy
3. **Chef Deployment Scripts** (setup-automate/): High complexity, need to replace with Ansible roles

### Assumptions

1. The Chef Automate and Chef Infra Server deployment is being replaced with an Ansible-based solution, not just migrating the deployment scripts to Ansible.
2. The InSpec tests are valuable and should be maintained in some form, either as InSpec tests called from Ansible or converted to Ansible-native tests.
3. The target environment will continue to be Ubuntu 20.04 or compatible.
4. The hardcoded credentials in the deployment scripts are for testing purposes only and will be replaced with secure credential management in the production environment.
5. The SSL certificate generation in the Ansible playbooks is for testing purposes only and will be replaced with proper certificate management in production.