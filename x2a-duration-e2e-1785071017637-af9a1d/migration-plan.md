# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests for compliance validation
4. Creating a unified Ansible-based infrastructure as code solution

Estimated timeline: 1-2 weeks for a small team (1-2 engineers), given the limited scope and existing Ansible components.

## Module Migration Plan

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need individual migration planning:

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
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for validating HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance
- `index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with Ansible provisioner
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the ansible_inspec module

### Security Considerations

- **SSL Configuration**: Maintain the security hardening in the Apache SSL configuration
  - Migration approach: Preserve the SSL protocol restrictions in the Ansible tasks
  
- **SSH Hardening**: Maintain the SSH security controls validated by InSpec tests
  - Migration approach: Create Ansible tasks that implement the same SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create Ansible roles that install and configure Chef Automate components or replace with pure Ansible solution
  
- **InSpec Integration**: Maintaining InSpec tests while migrating to Ansible
  - Mitigation: Use the ansible_inspec module to run InSpec tests from Ansible playbooks

- **Configuration Validation**: Ensuring the migrated Ansible playbooks produce identical system states
  - Mitigation: Use the existing InSpec tests to validate the migrated playbooks

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** (high value, moderate complexity)
   - Convert bash scripts to Ansible roles
   - Replace hardcoded credentials with Ansible Vault

2. **website_https** and **poodle_fix** (low risk, already Ansible)
   - Standardize playbook structure
   - Integrate with Ansible best practices
   - Maintain InSpec tests

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are intended to be maintained as part of the compliance strategy
3. The Chef Automate and Chef Server deployments are intended to be replaced with Ansible equivalents
4. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are to be preserved but standardized
5. The hardcoded credentials in the deployment scripts are for demonstration only and will be replaced with secure alternatives
6. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file