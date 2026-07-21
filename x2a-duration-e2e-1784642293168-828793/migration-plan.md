# MIGRATION FROM CHEF/BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks that need to be consolidated into a pure Ansible solution. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a more structured format
3. Ensuring InSpec tests continue to work with the new Ansible structure

Based on thorough analysis using file_search for Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), and PowerShell modules (.psd1), no traditional infrastructure-as-code modules were found. Instead, the repository contains bash scripts for Chef deployment and Ansible playbooks.

Given the limited scope (2 bash scripts and 2 Ansible playbooks), this migration could be completed in 1-2 days by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

Note: No traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) were found in the repository. The following components were identified:

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Server deployment, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure Apache web server with SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH configuration
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Create Ansible roles that perform the same configuration as the Chef Automate deployment scripts
  
- **Test Kitchen with Ansible**: Maintain but update configuration
  - Migration strategy: Update Test Kitchen configuration to work with the new Ansible structure

- **InSpec**: Maintain as the testing framework
  - Migration strategy: Keep InSpec tests but ensure they're properly integrated with the new Ansible workflow

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache
  - Migration approach: Maintain the same SSL configuration in the new Ansible roles
  
- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials
  - Migration approach: Replace hardcoded credentials with Ansible Vault or environment variables
  
- **Vault/secrets management**:
  - Hardcoded passwords in setup-automate scripts (userpassword='password')
  - SSL certificates generated and managed in the website_https.yml playbook
  - Migration approach: Use Ansible Vault for all credentials and sensitive data

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible
  - Mitigation strategy: Create an Ansible role that installs and configures Chef Server using the official packages
  
- **InSpec Integration**: Ensuring InSpec tests continue to work with the new Ansible structure
  - Mitigation strategy: Maintain the Test Kitchen configuration and update it to work with the new Ansible roles

### Migration Order

1. **chef-automate-deployment** (high value, moderate complexity)
   - Convert bash scripts to Ansible roles
   - Replace hardcoded credentials with Ansible Vault
   
2. **website-https** (low risk, already in Ansible)
   - Restructure into proper Ansible role format
   - Update Test Kitchen configuration
   
3. **poodle-fix** (low risk, already in Ansible)
   - Integrate into the website-https role as an optional task
   - Update tests to verify SSL configuration

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The InSpec tests are essential and must be maintained
3. The deployment scripts are intended for on-premises or cloud VMs
4. The target environment is Ubuntu 20.04
5. The hardcoded credentials in the scripts are for demonstration purposes only
6. The SSL configuration is important for security compliance
7. The Apache configuration is relatively simple and can be easily converted to an Ansible role
8. The Chef Automate and Chef Server deployment is the most complex part of the migration