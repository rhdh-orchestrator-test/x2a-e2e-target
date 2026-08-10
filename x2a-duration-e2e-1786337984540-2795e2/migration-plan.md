# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a proper Ansible project structure
3. Preserving the Chef InSpec testing capabilities within an Ansible workflow

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

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
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration and security
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH configuration testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a testing tool within Ansible workflow using ansible-test or molecule
- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that install and configure equivalent monitoring and configuration management tools

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only, which should be preserved in the migrated solution
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates, which should be replaced with a more robust certificate management solution in production
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username: jtonello
  - Password: password
  - Email: jtonello@chef.lab

### Technical Challenges

- **Chef InSpec Integration**: Preserving the compliance testing capabilities of InSpec within an Ansible-only workflow
  - Mitigation: Use Ansible's built-in assert module for basic tests and integrate InSpec as a separate step in CI/CD pipeline
  
- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem
  - Mitigation: Consider AWX/Tower for web UI and API, combined with tools like Prometheus/Grafana for monitoring

- **Configuration Drift Detection**: Chef Infra Server provides configuration drift detection
  - Mitigation: Implement regular Ansible runs with check mode and reporting

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Restructure existing playbooks into proper Ansible roles
   - Implement variable files to replace hardcoded values
   - Add documentation

2. **Chef Deployment Scripts** (Medium complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Implement Ansible Vault for credential storage
   - Test deployment on similar infrastructure

3. **Testing Framework** (High complexity)
   - Migrate from Test Kitchen to Molecule
   - Preserve InSpec tests but integrate them with Ansible workflow
   - Implement CI/CD pipeline integration

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README content
2. The Chef InSpec tests are valuable and should be preserved in some form
3. The target environment will continue to be Ubuntu-based systems
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The hardcoded credentials in the deployment scripts are examples and not actual production credentials
6. The Apache configuration in the Ansible playbooks represents the actual desired state for web servers