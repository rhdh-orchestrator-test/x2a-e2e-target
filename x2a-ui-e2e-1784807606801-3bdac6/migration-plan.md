# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities of Chef InSpec.

**Estimated Timeline**: 1-2 days for migration, given the small codebase and limited complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Maintain InSpec for compliance testing or consider migrating to Ansible's built-in assert module or other testing frameworks like Molecule's verifier
- **Vagrant**: Continue using Vagrant for local testing or consider containerized testing with Docker

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible roles.
- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these security checks are maintained.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management in production.
- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the playbooks

### Technical Challenges

- **Chef InSpec Integration**: Maintaining the InSpec testing capability while migrating to a pure Ansible solution. Consider using Ansible's built-in testing capabilities or integrating with other testing frameworks.
- **Chef Automate/Server Deployment**: Converting the bash scripts for Chef Automate and Chef Server deployment to Ansible roles. This may require significant testing to ensure proper functionality.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Convert to Ansible role structure with proper variables, templates, and handlers
2. **poodle_fix.yml** (low risk, already Ansible): Convert to Ansible role structure or integrate into the website_https role
3. **InSpec Tests** (moderate complexity): Maintain as-is or convert to equivalent Ansible testing framework
4. **Chef Deployment Scripts** (high complexity): Convert bash scripts to Ansible roles for Chef Automate and Chef Server deployment

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec tests are valuable and should be preserved in some form
3. The Chef deployment scripts are needed for the demonstration environment
4. The target environment will continue to be Ubuntu 20.04 or similar
5. No external dependencies or inventory files are required beyond what's in the repository
6. The migration will maintain the same functionality but with improved structure and maintainability