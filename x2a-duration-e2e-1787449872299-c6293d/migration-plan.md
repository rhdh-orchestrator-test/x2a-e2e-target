# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests while integrating them into an Ansible-native workflow

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains shell scripts and simple Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related shell scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec tests but integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible's native testing framework
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with the Ansible provisioner
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same configuration

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the Ansible migration.
- **SSH Hardening**: InSpec tests verify SSH security configurations. Ensure these tests continue to pass after migration.
- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires careful handling of the installation process and configuration
- **InSpec Integration**: Determining the best approach to integrate InSpec tests with Ansible (either keeping InSpec or migrating to Ansible's native testing)
- **Test Kitchen**: Deciding whether to replace Test Kitchen with Molecule or maintain it with the Ansible provisioner

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need review and potential refactoring
2. **Chef Server Deployment Script** (deploy-chef-server.sh): Medium complexity, convert to Ansible playbook
3. **Chef Automate Deployment Script** (deploy-automate.sh): Medium complexity, convert to Ansible playbook
4. **Testing Framework**: Integrate InSpec tests with Ansible workflow or migrate to Ansible-native testing

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."
2. The Chef Automate and Chef Infra Server deployment scripts are intended for educational/demonstration purposes and may not include all production-ready configurations.
3. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure credential management in production.
4. The InSpec tests are intended to demonstrate compliance automation alongside Ansible rather than being part of a comprehensive test suite.
5. The migration goal is to consolidate on Ansible while maintaining the educational/demonstration value of the repository.