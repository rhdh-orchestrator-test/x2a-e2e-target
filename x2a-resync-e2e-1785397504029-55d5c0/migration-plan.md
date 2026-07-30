# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests for compliance verification
4. Creating a unified Ansible-based workflow that preserves the compliance testing capabilities

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website configuration
- `chef-and-ansible/index.html`: Likely a sample HTML file for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec tests but integrate with Ansible workflow

### Security Considerations

- **SSL Configuration**: The repository includes SSL hardening (disabling SSLv3, enabling TLSv1.2)
  - Migration approach: Preserve these security configurations in Ansible tasks
  
- **Self-signed Certificates**: The playbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules (already in use)

- **Vault/secrets management**:
  - Hardcoded credentials in Bash scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the Bash scripts
  - Research Ansible Galaxy for existing Chef Automate deployment roles

- **InSpec Integration**: Maintaining InSpec tests while moving to pure Ansible
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests
  - Alternative: Use Molecule with InSpec verifier for testing

- **Test Kitchen Replacement**: Finding an equivalent testing framework
  - Mitigation: Migrate to Ansible Molecule for infrastructure testing

### Migration Order

1. **chef-automate-deployment** (high value, moderate complexity)
   - Create Ansible role for Chef Automate deployment
   - Implement Ansible Vault for credential storage

2. **website-https-configuration** (low risk, already Ansible)
   - Standardize playbook structure
   - Improve variable naming and organization
   - Add documentation

3. **ssl-poodle-vulnerability-fix** (low risk, already Ansible)
   - Consider merging with website-https-configuration as a role
   - Improve variable naming and organization

4. **Testing Framework** (moderate complexity)
   - Migrate from Test Kitchen to Molecule
   - Preserve InSpec tests

### Assumptions

1. The repository is primarily for demonstration purposes (as indicated by the README.md)
2. The Chef Automate deployment scripts are the primary target for migration to Ansible
3. The existing Ansible playbooks should be preserved but standardized
4. InSpec tests should be maintained for compliance verification
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. No complex Chef cookbooks or recipes need migration (none were found in the repository)
7. The hardcoded credentials in the Bash scripts are for demonstration only and will be replaced with Ansible Vault
8. The Apache configuration in the Ansible playbooks is relatively simple and can be preserved as-is