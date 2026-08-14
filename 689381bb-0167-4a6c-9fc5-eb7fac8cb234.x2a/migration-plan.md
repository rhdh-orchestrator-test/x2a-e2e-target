# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks used for demonstration purposes. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on standardizing the existing Ansible playbooks and converting the Chef Automate deployment scripts to Ansible.

**Estimated Timeline**: 1-2 weeks for a single engineer to complete the migration, including testing.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `tests/website_https_verify.rb`: Chef InSpec tests for verifying the HTTPS website deployment
- `index.html`: Sample HTML file for testing

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for Chef Automate deployment or remove if Chef Automate is no longer needed
- **Test Kitchen with Ansible**: Migrate to Molecule for Ansible role/playbook testing
- **Chef InSpec**: Can be retained for compliance testing or replaced with Ansible-native solutions like ansible-lint or integrated with tools like Compliance-as-Code

### Security Considerations

- **SSL/TLS Configuration**: The playbooks handle SSL configuration and POODLE vulnerability mitigation
  - Migration approach: Maintain the same security hardening in the migrated Ansible playbooks
  - Consider updating to include more recent TLS best practices (TLS 1.3 support)

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials
  - Migration approach: Replace with Ansible Vault for secure credential storage
  - Identify and secure the following credentials:
    - User password in deploy-automate.sh and deploy-chef-server.sh

- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Consider integrating with Let's Encrypt for production environments

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts
  - Research existing community roles for Chef Server deployment

- **InSpec Integration**: Maintaining the InSpec testing capabilities
  - Mitigation: Ensure the Ansible playbooks can be tested with InSpec or migrate to Ansible-native testing

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Refactor to follow Ansible best practices
   - Convert to a proper role structure

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Refactor to follow Ansible best practices
   - Consider merging with website_https as a security enhancement option

3. **Chef deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible roles
   - Implement secure credential handling with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The Chef Automate and Chef Server deployment scripts are still needed in the migrated solution
3. The InSpec tests should be preserved for compliance verification
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The hardcoded credentials in the deployment scripts are for demonstration only and will be replaced with secure alternatives
6. The self-signed certificates are acceptable for the demonstration environment but may need to be replaced with trusted certificates in production