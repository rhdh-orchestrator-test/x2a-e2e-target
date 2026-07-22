# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef infrastructure setup scripts and Ansible playbooks focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting of two Ansible playbooks for web server configuration and two bash scripts for Chef server/Automate deployment. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which need minimal changes) and moderate complexity for converting the Chef server deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

Based on thorough file searches (`file_search(pattern="**/manifests/init.pp")`, `file_search(pattern="**/recipes/default.rb")`, and `file_search(pattern="**/*.psd1")`), no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository.

The repository contains:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant, targeting Ubuntu 20.04
- `tests/website_https_verify.rb`: InSpec tests for verifying HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec compliance profile for SSH security configuration
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform setup
- **Chef Server CLI**: Replace with Ansible roles for configuration management platform setup
- **InSpec (version not specified)**: Retain InSpec for compliance testing, integrate with Ansible using the ansible_inspec module or through CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated Ansible playbooks.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. Ensure this security control is implemented in the migrated Ansible playbooks.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No encrypted data or vault usage detected in current implementation

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require creating roles and playbooks that perform equivalent package installation and configuration.
  - Mitigation: Create dedicated Ansible roles for Chef server deployment or consider replacing with alternative configuration management solutions.

- **InSpec Integration**: Maintaining the InSpec tests while migrating to pure Ansible requires proper integration.
  - Mitigation: Use the ansible_inspec module or integrate InSpec tests into CI/CD pipelines that run after Ansible playbook execution.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor updates for best practices and integration with the rest of the Ansible codebase.

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires converting bash scripts to Ansible playbooks or deciding on an alternative approach for configuration management platform deployment.

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, potentially replacing Chef Automate/Server deployment with equivalent Ansible Tower/AWX setup.

2. InSpec will continue to be used for compliance testing, even after migration to Ansible.

3. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and only need minor adjustments to align with best practices.

4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions.

5. The hardcoded credentials in the Chef deployment scripts are for demonstration purposes only and will be replaced with proper secret management in the migrated solution.

6. The repository appears to be primarily for demonstration/educational purposes rather than production use, based on the README content and simplified configurations.