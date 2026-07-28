# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring the migration preserves security configurations and testing capabilities

The estimated timeline for this migration is 1-2 weeks given the limited scope and complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys only Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with Ansible provisioner
- **InSpec**: Maintain InSpec for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Migration approach: Preserve the existing Ansible task that enforces TLSv1.2 and disables older protocols
  
- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions
  - Migration approach: Ensure the Ansible playbooks include SSH hardening tasks that align with the InSpec tests

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Maintain this functionality but consider adding support for Let's Encrypt certificates

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation strategy: Create an Ansible role that installs and configures Chef Automate using the official installation methods
  
- **InSpec Integration**: Ensuring InSpec tests continue to work with the Ansible-managed infrastructure
  - Mitigation strategy: Maintain the InSpec tests and integrate them into the Ansible workflow using post-tasks or a separate playbook

- **Configuration Validation**: Ensuring the migrated Ansible playbooks produce identical system configurations
  - Mitigation strategy: Use InSpec tests to validate the configurations before and after migration

### Migration Order

1. **chef-server-deploy script** (Priority 1): Convert to Ansible playbook first as it's simpler than the Automate deployment
2. **chef-automate-deploy script** (Priority 2): Convert to Ansible playbook, building on the Chef Server playbook
3. **Standardize existing Ansible playbooks** (Priority 3): Ensure website_https.yml and poodle_fix.yml follow best practices

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) will be preserved with minimal changes
2. InSpec will continue to be used for compliance testing alongside Ansible
3. The deployment scripts are intended for on-premises or generic cloud VMs
4. The hardcoded credentials in the deployment scripts are for testing purposes only
5. The repository is primarily for demonstration/example purposes rather than production use
6. Test Kitchen will continue to be used for testing the Ansible playbooks
7. The target environment will remain Ubuntu 20.04 or similar Linux distributions