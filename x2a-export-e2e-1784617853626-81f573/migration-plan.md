# MIGRATION FROM MIXED TECHNOLOGIES TO ANSIBLE

## Executive Summary

This repository contains a mix of technologies including Ansible playbooks, Chef InSpec tests, and bash scripts for Chef product deployment. The primary focus appears to be demonstrating how Chef InSpec can be used for compliance testing with Ansible deployments. The migration scope is relatively small, focusing on standardizing all components to Ansible while maintaining the existing functionality.

**Timeline Estimate**: 2-3 weeks for a small team (1-2 engineers)
**Complexity**: Medium

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

No traditional modules with manifests/init.pp (Puppet), recipes/default.rb (Chef), or .psd1 manifests (PowerShell) were found in the repository. The repository contains the following components that need migration:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration and security
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain as a separate testing tool
- **Test Kitchen with kitchen-ansible**: Replace with Molecule for Ansible-native testing or update to use the latest version
- **Apache 2.4.41**: Maintain version pinning or update to latest stable version
- **OpenSSL**: Maintain for certificate generation or consider using Ansible's crypto modules

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be maintained or enhanced in the migrated solution.
- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained in the migrated solution.
- **Vault/secrets management**: 
  - No encrypted secrets were found in the repository
  - Hardcoded credentials exist in the deploy scripts (username, password)
  - SSL/TLS certificate references are present but certificates are generated during deployment
  - Total credentials detected: 2 (username/password in deploy scripts)

### Technical Challenges

- **InSpec Test Migration**: The InSpec tests provide valuable security and compliance checks. Consider:
  - Option 1: Keep InSpec as a testing tool alongside Ansible
  - Option 2: Migrate tests to Ansible-native testing frameworks like Molecule with testinfra
  - Option 3: Implement equivalent checks using Ansible's assert module

- **Chef Automate/Server Deployment**: The bash scripts deploy Chef Automate and Chef Infra Server. Consider:
  - Option 1: Create equivalent Ansible roles for deploying Chef products
  - Option 2: Maintain bash scripts if Chef deployment is still needed
  - Option 3: Replace with alternative compliance and automation tools in the Ansible ecosystem

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and update to current Ansible best practices
2. **poodle_fix.yml** (low risk, already Ansible): Review and update to current Ansible best practices
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing or integrate with Ansible workflow
4. **Chef Deployment Scripts** (high complexity): Convert to Ansible roles or replace functionality

### Assumptions

1. The primary goal is to maintain or enhance the existing functionality while standardizing on Ansible.
2. The InSpec tests are valuable and their functionality should be preserved in some form.
3. The Chef Automate and Chef Server deployment scripts may or may not be needed in the future state.
4. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
5. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.
7. No traditional Puppet modules, Chef cookbooks, or PowerShell modules exist in this repository, as confirmed by file searches.