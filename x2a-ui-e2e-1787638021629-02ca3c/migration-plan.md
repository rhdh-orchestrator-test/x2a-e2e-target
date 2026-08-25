# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec for compliance testing while integrating it with pure Ansible workflows

**Estimated Timeline**: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope of the repository.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **Chef InSpec**: Maintain as a compliance testing tool, but integrate with Ansible workflows

### Security Considerations

- **SSL/TLS Configuration**: The repository includes security hardening for Apache SSL configuration
  - Migration approach: Preserve the security hardening in Ansible playbooks
  - Enhance with Ansible security roles from Ansible Galaxy

- **Self-signed Certificates**: The playbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules (already in use)
  - Consider adding option for Let's Encrypt integration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining Chef InSpec for compliance testing while moving to pure Ansible
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests from Ansible

- **Chef Automate/Server Deployment**: Converting bash scripts to idempotent Ansible playbooks
  - Mitigation: Use existing Ansible roles from the community for Chef Server deployment or create custom roles based on the installation steps

### Migration Order

1. **Chef Server/Automate Deployment Scripts** (high value, moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement Ansible Vault for credential management

2. **Test Kitchen Configuration** (low risk, high value)
   - Migrate to Ansible Molecule for testing
   - Preserve InSpec tests

3. **Existing Ansible Playbooks** (low complexity)
   - Review and enhance existing playbooks
   - Ensure idempotence and best practices

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments
2. The Chef InSpec tests are to be preserved as they demonstrate compliance automation
3. The target environment is Ubuntu 20.04 as specified in the Test Kitchen configuration
4. The deployment scripts are intended for both on-premises and cloud environments
5. No external dependencies or modules beyond what's visible in the repository
6. No complex data structures or Hiera data to migrate
7. No existing Chef cookbooks to convert (only deployment scripts)
8. The Apache configuration is relatively simple and can be directly translated to Ansible