# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while integrating them into a cohesive Ansible structure
3. Maintaining the Chef InSpec tests for compliance validation but integrating them with Ansible

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

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

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test for validating SSH security configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec tests but integrate with Ansible using the ansible_inspec module or Molecule verifier

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use)

- **SSH Hardening**: InSpec tests validate SSH security configurations.
  - Migration approach: Create Ansible tasks to implement the same SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture.
  - Mitigation: Create an Ansible role that installs and configures Chef Automate using the official installation methods

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible.
  - Mitigation: Use Ansible's capabilities to run InSpec tests as part of playbook execution or use Molecule with InSpec verifier

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Refactor into proper Ansible roles and structure
   - Update Test Kitchen configuration to use Molecule

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Moderate complexity
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Replace hardcoded credentials with Ansible Vault

3. **Testing Framework** - Moderate complexity
   - Integrate InSpec tests with Ansible using appropriate modules
   - Set up CI/CD pipeline for automated testing

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.
2. The Chef Automate and Chef Server deployment scripts are intended for on-premises or cloud VM deployment.
3. The InSpec tests are meant to validate both the Ansible-deployed configurations and potentially other systems.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced in a production environment.
5. The target environment is Ubuntu 20.04 based on the Test Kitchen configuration.
6. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes beyond structural reorganization.