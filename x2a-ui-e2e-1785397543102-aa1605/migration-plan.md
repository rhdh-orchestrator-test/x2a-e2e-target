# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing them
3. Maintaining Chef InSpec tests for compliance validation
4. Creating a unified Ansible-based infrastructure management solution

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains a limited number of scripts and playbooks

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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assertion modules
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with the Ansible provisioner
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for Chef server deployment, or consider migrating completely to Ansible AWX/Tower for similar functionality

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: The InSpec tests verify SSH security settings. Maintain these tests and implement corresponding Ansible tasks
- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly but should be managed securely in production

### Technical Challenges

- **Chef InSpec Integration**: Determining how to maintain InSpec tests while standardizing on Ansible
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests from Ansible
  
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible
  - Mitigation: Create an Ansible role that performs the same steps as the bash scripts

- **Test Kitchen to Molecule Migration**: If moving completely to Ansible ecosystem
  - Mitigation: Create equivalent Molecule scenarios for existing Test Kitchen tests

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml): Low risk as they're already in Ansible format
   - Standardize variable naming and structure
   - Add documentation
   - Convert to roles if appropriate

2. **Chef Deployment Scripts** (setup-automate/*.sh): Medium complexity
   - Create Ansible roles to replace the bash scripts
   - Use Ansible Vault for credentials
   - Add idempotency checks

3. **Testing Framework**: Medium complexity
   - Decide whether to maintain Test Kitchen or migrate to Molecule
   - Ensure InSpec tests continue to work with the new deployment method

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. The InSpec tests are valuable and should be preserved
3. The goal is to standardize on Ansible while maintaining the same functionality
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The hardcoded credentials in the deployment scripts are for demonstration only
6. The SSL certificates are self-signed for testing purposes