# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while ensuring they follow best practices
3. Integrating the Chef InSpec tests with Ansible or converting them to equivalent Ansible testing frameworks

Given the limited scope, this migration is estimated to be **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS**.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure website with Apache and SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec Tests**: Either integrate with Ansible using the `inspec` module or convert to equivalent Ansible testing frameworks like Molecule with Testinfra

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained in the migrated Ansible playbooks.
- **SSH Hardening**: The InSpec tests check for SSH security compliance. Ensure these checks are maintained in the migrated testing framework.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require understanding of Chef Automate architecture and configuration options.
  - Mitigation: Create an Ansible role that handles the installation and configuration of Chef Automate, or consider using the official Chef Automate Ansible role if available.

- **InSpec Test Integration**: Integrating InSpec tests with Ansible or converting them to equivalent testing frameworks.
  - Mitigation: Use Ansible's `inspec` module to run InSpec tests, or convert the tests to Molecule with Testinfra.

### Migration Order

1. **chef-automate-deployment** (Medium complexity, high value)
   - Convert Bash scripts to Ansible playbooks
   - Move hardcoded credentials to Ansible Vault
   - Create roles for Chef Automate and Chef Infra Server deployment

2. **website-https** (Low complexity, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Ensure idempotence
   - Move to role-based structure

3. **poodle-fix** (Low complexity, already in Ansible)
   - Review and refactor according to Ansible best practices
   - Consider merging with website-https role as a security hardening task

4. **Testing Framework** (Medium complexity)
   - Decide on testing approach (keep InSpec or migrate to Molecule/Testinfra)
   - Set up CI/CD pipeline for automated testing

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distribution
2. Vagrant will continue to be used for development/testing environments
3. The Chef Automate and Chef Infra Server deployment is for demonstration purposes and not production use
4. The InSpec tests are valuable and should be preserved in some form
5. The repository is primarily for educational/demonstration purposes rather than production infrastructure
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data migration is required as this appears to be primarily infrastructure code
8. The Apache configuration and SSL setup are relatively standard and don't have custom modules or configurations