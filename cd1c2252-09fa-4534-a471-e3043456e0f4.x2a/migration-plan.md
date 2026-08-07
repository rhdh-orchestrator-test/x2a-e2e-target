# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while standardizing their structure
3. Maintaining the Chef InSpec tests for compliance validation

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** due to the limited number of components and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Chef Server CLI**: Replace with Ansible roles for configuration management server deployment
- **Test Kitchen with Ansible**: Maintain or migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing or consider migrating to Ansible's built-in assert module or other testing frameworks

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook specifically addresses SSL/TLS security by enforcing TLSv1.2. This security hardening should be preserved in the migration.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. Ensure this security check is maintained.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible will require creating roles and tasks that replicate the Chef Automate CLI functionality. This may require additional research on Chef Automate's API or deployment options.
- **InSpec Integration**: Maintaining the InSpec tests while standardizing on Ansible may require setting up a workflow that allows Ansible to trigger InSpec tests or migrating tests to Ansible's native testing capabilities.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Standardize structure and variable naming.
2. **Chef Server Deployment** (deploy-chef-server.sh): Moderate complexity, create Ansible role to replace bash script.
3. **Chef Automate Deployment** (deploy-automate.sh): Higher complexity, create Ansible role to replace bash script with both Automate and Infra Server components.
4. **Testing Framework**: Migrate Test Kitchen configuration to Ansible Molecule while preserving InSpec tests.

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes.
2. The InSpec tests should be preserved for compliance validation rather than being converted to another testing framework.
3. The Chef Automate and Chef Server deployment scripts are used for setting up infrastructure management tools, which will be replaced by Ansible Tower/AWX or similar.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.