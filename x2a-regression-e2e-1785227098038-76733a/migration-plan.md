# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Chef Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a standardized structure
3. Preserving the InSpec testing capabilities within an Ansible framework

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains deployment scripts and simple Ansible playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec tests but integrate with Ansible using ansible_inspec module or convert to Ansible assert modules

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be preserved in the migrated Ansible roles.
- **SSH Hardening**: The ssh_profile.rb InSpec test checks for secure SSH configuration (disabling root login). This should be implemented as an Ansible role with appropriate tasks.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **Vault/secrets management**:
  - Hardcoded credentials in Chef deployment scripts (username, password)
  - Consider migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible will require creating tasks that properly configure the Chef Automate server, which may involve complex configuration steps.
  - Mitigation: Create a dedicated Ansible role for Chef Automate deployment with appropriate handlers and idempotent tasks.

- **InSpec Integration**: Preserving the compliance testing capabilities of InSpec within an Ansible workflow.
  - Mitigation: Use the ansible_inspec module or convert tests to equivalent Ansible assert statements.

- **Testing Framework**: Migrating from Test Kitchen to Ansible Molecule for testing.
  - Mitigation: Create Molecule scenarios that replicate the existing Test Kitchen tests.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Refactor into proper Ansible roles with variables, handlers, and tasks
   - Implement best practices for Ansible structure

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium risk
   - Create integration with Ansible using ansible_inspec module
   - Alternatively, convert to Ansible assert statements

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement idempotent tasks to replace bash script commands
   - Use Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README mentioning "working examples" and "how-tos".
2. The Chef deployment scripts are intended for initial setup only and not ongoing configuration management.
3. The InSpec tests are meant to verify compliance after configuration rather than being part of a continuous compliance framework.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
6. The Apache configuration in the Ansible playbooks is for demonstration purposes and may need enhancement for production use.
7. The repository does not contain actual Chef cookbooks or recipes that need migration, only deployment scripts for Chef infrastructure.