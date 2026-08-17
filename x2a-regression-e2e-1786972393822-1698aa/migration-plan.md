# MIGRATION FROM CHEF/ANSIBLE HYBRID TO ANSIBLE

## Executive Summary

This repository contains a hybrid environment with Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains deployment scripts and simple Ansible playbooks

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Maintain InSpec for compliance testing, but integrate with Ansible workflow

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible playbooks.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing proper certificate management.
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be replaced with Ansible Vault:
  - Username/password in deploy-automate.sh and deploy-chef-server.sh
  - Consider using Ansible Vault for storing sensitive information

### Technical Challenges

- **Chef-specific Functionality**: The Chef Automate and Chef Server deployment scripts perform Chef-specific operations that need to be replaced with Ansible equivalents or alternative solutions.
- **InSpec Integration**: Maintaining InSpec testing capabilities within an Ansible-only workflow will require proper integration.
- **Configuration Management**: Replacing Chef's configuration management capabilities with Ansible's approach.

### Migration Order

1. **website_https and poodle_fix playbooks** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbooks
   - Convert inline templates to separate template files
   - Implement Ansible best practices (roles, variables, etc.)

2. **InSpec Tests** (low risk, can be maintained)
   - Integrate InSpec tests with Ansible workflow
   - Replace Test Kitchen with Ansible Molecule

3. **Chef Deployment Scripts** (moderate complexity)
   - Create Ansible roles for system preparation (hostname, sysctl)
   - Develop alternative configuration management approach using Ansible

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments.
2. The InSpec tests are intended to be maintained as part of the compliance automation strategy.
3. There are no additional Chef cookbooks or recipes beyond what's visible in the repository.
4. The target environment will continue to be Ubuntu-based systems.
5. The migration aims to completely eliminate Chef dependencies in favor of an Ansible-only approach.
6. The current Ansible playbooks (website_https.yml and poodle_fix.yml) are functional and can be used as a reference for the migration style.