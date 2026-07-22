# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Preserving InSpec testing functionality by integrating with Ansible

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository already contains Ansible playbooks, but requires standardization and conversion of deployment scripts

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, generates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user creation, organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file (appears to be unused, as content is defined in the playbook)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles
- **InSpec**: Either:
  - Option 1: Integrate InSpec tests with Ansible using the `ansible_inspec` module
  - Option 2: Convert InSpec tests to Ansible assertions or Molecule verifiers
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives like AWX

### Security Considerations

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab
- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only, which should be preserved in the migration
- **SSH Hardening**: The InSpec test verifies that SSH root login is disabled, which should be enforced in the migrated Ansible roles
- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh (username, password, email)
  - Self-signed SSL certificates generated in website_https.yml

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible verification methods may require additional effort
- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality (Ansible Automation Platform, AWX, or other tools)
- **Test Kitchen Integration**: Ensuring that the current testing workflow is preserved when migrating to Ansible Molecule

### Migration Order

1. **website_https.yml** (Priority 1): Convert to Ansible role with proper structure (low risk, already Ansible)
2. **poodle_fix.yml** (Priority 1): Convert to Ansible role or include in website_https role (low risk, already Ansible)
3. **InSpec Tests** (Priority 2): Convert to Ansible Molecule tests or integrate with Ansible (moderate complexity)
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible playbooks for deploying Ansible Automation Platform or AWX (higher complexity)

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
2. Vagrant will continue to be used for development/testing environments
3. The simple "Hello World" website is a placeholder and not a production application
4. The self-signed certificates are for testing only and would be replaced with proper certificates in production
5. The Chef Automate and Chef Infra Server deployment is for infrastructure management that will be replaced by Ansible
6. The InSpec tests are valuable and should be preserved in some form
7. No external dependencies or integrations beyond what's visible in the repository