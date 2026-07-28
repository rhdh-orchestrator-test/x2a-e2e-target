# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure setup. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The main focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure automation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Configures hostname, system parameters, downloads and deploys Chef Automate, creates users and organizations

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Configures hostname, system parameters, downloads and deploys Chef Infra Server, creates users and organizations

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Convert to Ansible assert tasks or maintain as InSpec tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Migration consideration: Convert to Ansible assert tasks or maintain as InSpec tests.
- `chef-and-ansible/index.html`: Sample HTML file for testing web server. Migration consideration: Include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec Tests**: Two options:
  1. Convert to Ansible assert tasks and include in playbooks
  2. Keep as InSpec tests but integrate with Ansible using the `community.general.inspec` module
- **Chef Automate/Infra Server**: Replace with AWX/Ansible Tower or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible playbooks.
- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the playbook
  - Migration should use Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions while maintaining the same level of compliance validation.
  - Mitigation: Use the `community.general.inspec` module to run existing InSpec tests from Ansible.
  
- **Chef Automate Replacement**: Finding an equivalent Ansible-based solution for the functionality provided by Chef Automate.
  - Mitigation: Consider AWX/Ansible Tower with compliance scanning tools like OpenSCAP.

### Migration Order

1. **website-https playbook** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle-fix playbook** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec tests** (moderate complexity): Either integrate with Ansible using the inspec module or convert to Ansible assertions
4. **Chef deployment scripts** (high complexity): Replace with Ansible playbooks for deploying AWX/Ansible Tower or other management platform

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies
2. InSpec tests are valuable and their functionality should be preserved
3. The deployment scripts for Chef Automate/Infra Server will be replaced with equivalent Ansible management platform setup
4. The target environment will remain Ubuntu 20.04 on Vagrant VMs
5. No external data sources or complex integrations exist beyond what's visible in the repository
6. The hardcoded credentials in the setup scripts are for testing only and will be replaced with proper secret management
7. The self-signed certificates are for testing only and will be replaced with proper certificate management in production