# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while standardizing them
3. Maintaining the Chef InSpec tests for compliance validation

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the repository primarily contains deployment scripts and simple Ansible playbooks rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to address POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate if still needed, or consider migrating to alternative solutions like AWX/Ansible Tower
- **Test Kitchen with Ansible**: Maintain Test Kitchen for testing or migrate to Ansible Molecule for testing Ansible roles
- **Chef InSpec**: Keep InSpec for compliance testing as it works well with Ansible, or consider migrating to Ansible's built-in assert module for simpler tests

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: The InSpec tests verify SSH security configurations. Maintain these tests and implement corresponding Ansible tasks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible Vault for storing pre-generated certificates
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture. Consider using the official Chef Automate Ansible role if available, or create a custom role
- **InSpec Integration**: Ensure that InSpec tests continue to work with the migrated Ansible playbooks. This may require adjustments to the test execution workflow

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need standardization
2. **Chef Automate Deployment Scripts**: Medium complexity, requires converting Bash scripts to Ansible playbooks
3. **Test Kitchen Configuration**: Update to work with the new Ansible structure

### Assumptions

1. The repository is primarily used for demonstration purposes as indicated by the README ("working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams")
2. The Chef Automate deployment is still required after migration (rather than being replaced by Ansible Tower/AWX)
3. InSpec will continue to be used for compliance testing alongside Ansible
4. The target environment will remain Ubuntu 20.04 or similar Debian-based distributions
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with proper secret management in production

## Migration Tasks

1. **Standardize Existing Ansible Playbooks**:
   - Review and update website_https.yml and poodle_fix.yml to follow Ansible best practices
   - Convert inline templates to separate template files
   - Implement proper variable management

2. **Convert Chef Automate Deployment Scripts**:
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Move hardcoded variables to Ansible Vault
   - Implement idempotent deployment logic

3. **Update Testing Framework**:
   - Maintain Test Kitchen configuration or migrate to Molecule
   - Ensure InSpec tests continue to work with the migrated playbooks

4. **Documentation**:
   - Update README files to reflect the new Ansible-based approach
   - Document the migration process and any changes to the workflow