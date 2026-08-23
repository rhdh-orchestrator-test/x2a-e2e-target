# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains straightforward deployment scripts and basic Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

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
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec tests for compliance validation, integrate with Ansible using the `ansible.builtin.shell` module or consider migrating to Ansible's built-in assertion modules
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Server**: Replace with Ansible Automation Platform or other Ansible management solution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented
  
- **SSH Hardening**: InSpec tests validate SSH security configurations
  - Migration approach: Create Ansible role for SSH hardening based on InSpec requirements

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Use Ansible Vault to secure credentials

### Technical Challenges

- **Chef InSpec Integration**: Determining how to maintain compliance testing with InSpec or migrate to native Ansible testing
  - Mitigation: Create wrapper playbooks that run InSpec tests or migrate tests to Ansible assertions

- **Chef Automate Replacement**: Identifying appropriate Ansible management platform
  - Mitigation: Evaluate Ansible Automation Platform or AWX as replacements for Chef Automate

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/*.yml) - Low risk, already in Ansible format
   - Refactor to use Ansible best practices (roles, variables, etc.)
   - Enhance with idempotency improvements

2. **Chef Deployment Scripts** (setup-automate/*.sh) - Medium complexity
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management with Ansible Vault

3. **Testing Framework** - Medium complexity
   - Migrate from Test Kitchen to Ansible Molecule
   - Maintain InSpec tests or convert to Ansible assertions

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. InSpec tests are valuable and should be preserved in some form
3. The Chef Automate/Server deployment scripts are the primary targets for migration
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex data structures or state management requirements
6. No CI/CD pipeline integration requirements specified
7. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
8. The hardcoded credentials in the deployment scripts are for demonstration only and not used in production