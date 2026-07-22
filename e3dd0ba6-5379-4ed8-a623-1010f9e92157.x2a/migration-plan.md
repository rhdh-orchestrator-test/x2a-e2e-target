# MIGRATION FROM BASH SCRIPTS AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains Ansible playbooks and bash scripts for Chef Automate/Infra Server deployment. After thorough analysis, no Chef cookbooks, Puppet modules, or PowerShell modules were found. The migration scope is focused on standardizing all infrastructure as code to Ansible, with an estimated timeline of 1-2 weeks for a single engineer due to the relatively small codebase.

## Module Migration Plan

This repository contains Ansible playbooks and bash scripts that need individual migration planning:

### MODULE INVENTORY

After thorough verification using file_search for patterns including "**/recipes/default.rb", "**/manifests/init.pp", and "**/*.psd1", no Chef cookbooks, Puppet modules, or PowerShell modules were found in this repository.

The following searches were performed with no results:
- `**/recipes/default.rb` - No Chef cookbooks found
- `**/recipes/*.rb` - No Chef recipe files found
- `**/manifests/init.pp` - No Puppet modules found
- `**/*.pp` - No Puppet manifest files found
- `**/*.psd1` - No PowerShell modules found
- `**/*.ps1` - No PowerShell scripts found
- `**/metadata.rb` - No Chef cookbook metadata found
- `**/metadata.json` - No module metadata found

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address
- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate if still needed, or migrate to alternative compliance solutions
- **Chef InSpec**: Maintain as-is for compliance testing, as InSpec works well with Ansible
- **Apache 2.4.41**: Continue using the same version in Ansible playbooks
- **OpenSSL**: Continue using for certificate generation

### Security Considerations
- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert to an Ansible role with appropriate handlers
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Create an Ansible role for certificate management with options for self-signed or proper CA-signed certificates

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login configuration
  - Migration approach: Create an Ansible role for SSH hardening that satisfies the InSpec tests

### Technical Challenges
- **Challenge 1**: Maintaining InSpec tests while migrating deployment scripts
  - Mitigation: Keep InSpec tests as-is and ensure new Ansible roles satisfy the same tests

- **Challenge 2**: Handling Chef Automate deployment in Ansible
  - Mitigation: Create a comprehensive Ansible role for Chef Automate deployment or consider migrating to alternative compliance solutions

### Migration Order
1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Convert to proper Ansible roles with better variable management and modularization
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks/roles

### Assumptions
1. The Chef Automate and Chef Infra Server deployment is still required in the target environment
2. InSpec will continue to be used for compliance testing
3. The target environment will remain Ubuntu 20.04 or compatible
4. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives
5. The self-signed certificates in the website_https.yml playbook are for testing only and may need to be replaced with proper CA-signed certificates in production