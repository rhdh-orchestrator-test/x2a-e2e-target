# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a proper Ansible project structure
3. Preserving the InSpec testing capabilities within an Ansible workflow

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL protocol configuration

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom test modules
  - Option 2: Integrate InSpec with Ansible using the inspec_exec module from community.general collection
  - Option 3: Use Molecule for testing Ansible roles with InSpec verifier

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific CI/CD pipeline using GitHub Actions or similar

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for web UI, inventory management, and job scheduling
  - Option 2: GitLab CI/CD with Ansible for configuration management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should preserve:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (disabling SSLv3, enabling TLSv1.2)
  - Apache SSL module activation

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Maintain testing capabilities for SSH configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Testing Integration**: Maintaining compliance testing capabilities while migrating to Ansible
  - Mitigation: Use ansible.builtin.assert or community.general.inspec_exec module to run existing InSpec tests

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Map Chef Server features to Ansible AWX/Tower or alternative solutions

- **Test Kitchen Workflow**: Preserving the testing workflow currently implemented with Test Kitchen
  - Mitigation: Implement equivalent testing workflow using Molecule or ansible-test

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Restructure into proper Ansible role format
   - Add documentation and variables

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Restructure into proper Ansible role format
   - Consider merging with website_https as a security enhancement

3. **InSpec tests** (medium complexity)
   - Integrate with Ansible testing framework
   - Ensure tests run against playbook outputs

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement variable handling with Ansible Vault for credentials

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, not production deployments
2. The InSpec tests are essential and must be preserved in some form
3. The Chef Automate and Chef Infra Server deployments are needed in the migrated solution
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distribution
5. The migration will consolidate all components into a single Ansible project structure
6. No external dependencies or integrations beyond what's visible in the repository
7. The Test Kitchen configuration is used for local testing only, not in CI/CD pipelines