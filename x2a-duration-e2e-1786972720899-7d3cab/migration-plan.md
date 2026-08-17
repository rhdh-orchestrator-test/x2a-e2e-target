# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining the InSpec testing framework for compliance validation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for validating HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Test Kitchen with Ansible**: Maintain or migrate to Ansible Molecule for testing
- **InSpec**: Maintain as-is for compliance testing, or consider migrating to Ansible's built-in assert module where appropriate

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests validate SSH security configurations. Maintain these tests and implement corresponding Ansible tasks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **Chef Automate/Server Deployment**: Converting the Chef deployment scripts to Ansible will require:
  - Finding or creating Ansible roles for Chef Automate/Server deployment
  - Implementing proper idempotence for installation steps
  - Managing Chef user and organization creation through Ansible

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible playbooks
  - Consider implementing Ansible callback plugins for InSpec integration
  - Maintain test coverage during migration

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already in Ansible format)
   - Standardize and optimize existing playbooks (website_https.yml, poodle_fix.yml)
   - Implement Ansible best practices (roles, variables, etc.)

2. **Chef Deployment Scripts** (Medium complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement variable management with Ansible Vault for credentials

3. **Testing Framework** (Low risk, maintain as-is initially)
   - Migrate Test Kitchen configuration to Molecule if needed
   - Maintain InSpec tests for compliance validation

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the main README.md
2. The Chef deployment scripts are used for setting up Chef infrastructure, not for actual configuration management
3. InSpec is the preferred testing framework for compliance validation
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The existing Ansible playbooks are functional and follow basic Ansible practices
7. No external dependencies or complex infrastructure are required beyond what's explicitly defined in the repository