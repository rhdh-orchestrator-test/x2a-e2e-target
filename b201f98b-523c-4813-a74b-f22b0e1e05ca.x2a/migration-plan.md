# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on infrastructure automation and compliance testing. The primary migration scope involves:

1. Chef Automate and Chef Infra Server deployment scripts (in the setup-automate directory)
2. Chef InSpec compliance tests that are currently used alongside Ansible playbooks (in the chef-and-ansible/tests directory)

The migration complexity is relatively low as the repository already contains Ansible playbooks that can be used as a foundation. The estimated timeline for migration is 1-2 weeks, primarily focused on converting the Chef server deployment scripts to Ansible and ensuring the InSpec tests continue to work with the new Ansible implementation.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts with Chef server deployment
    - Key Features: User and organization creation, server configuration

- **website-https-configuration**:
    - Description: Ansible playbook for configuring a secure website with SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying website HTTPS and SSH security configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH security compliance checks

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples (companion to a white paper)
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a compliance testing tool that works with Ansible (already demonstrated in the repository)
- **Test Kitchen**: Replace with Ansible-native testing tools like Molecule, or continue using Test Kitchen with the Ansible provisioner
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solution

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening implemented in the poodle_fix.yml playbook
- **SSH Security**: The SSH compliance tests must continue to be enforced in the migrated solution
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef server deployment scripts (username, password)
  - SSL certificates generated and managed in the Ansible playbooks
  - Recommendation: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible playbooks will require understanding of Chef server architecture and equivalent Ansible automation
- **InSpec Integration**: Ensuring the InSpec tests continue to work with the new Ansible implementation
- **Test Kitchen**: Deciding whether to keep Test Kitchen with Ansible provisioner or migrate to Molecule

### Migration Order

1. **website-https-configuration** (already in Ansible, no migration needed)
2. **poodle-vulnerability-fix** (already in Ansible, no migration needed)
3. **chef-automate-deployment** (convert Bash scripts to Ansible playbooks)
4. **inspec-compliance-tests** (ensure they work with the new Ansible implementation)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning it's companion to a white paper.
2. The Chef InSpec tests are intended to be used with Ansible playbooks, not Chef cookbooks.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in a production environment.
4. The migration goal is to eliminate Chef server/Automate dependencies while maintaining the InSpec testing capabilities.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.