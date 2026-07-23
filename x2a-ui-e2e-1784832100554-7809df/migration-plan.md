# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while standardizing their structure
3. Maintaining the Chef InSpec testing capabilities within the Ansible workflow

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers), given the limited scope and straightforward nature of the components.

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
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance checks

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing but integrate with Ansible using the ansible_inspec module or ansible-test
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt Test Kitchen to work with pure Ansible
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for Chef server deployment or migrate completely to Ansible AWX/Tower

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests verify SSH security configurations. Maintain these tests and implement corresponding Ansible tasks
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - SSL certificate generation and management
  - Migration should implement Ansible Vault for all credentials

### Technical Challenges

- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible requires proper integration between the two tools
  - Mitigation: Use the ansible_inspec module or implement a custom Ansible callback plugin
  
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible requires careful handling of Chef-specific commands
  - Mitigation: Create an Ansible role that wraps the Chef installation commands or consider migrating to Ansible AWX/Tower

- **Test Kitchen Replacement**: Test Kitchen is currently used for testing Ansible playbooks
  - Mitigation: Migrate to Ansible Molecule for a more native Ansible testing experience

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need standardization
2. **InSpec Test Integration**: Moderate complexity, ensure tests continue to work with pure Ansible
3. **Chef Server Deployment Scripts**: High complexity, requires converting bash scripts to Ansible or deciding on a replacement strategy

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments (based on README content)
2. The InSpec tests are essential and must be preserved in the migration
3. The Chef Automate/Infra Server deployment may be replaced entirely with Ansible AWX/Tower
4. The hardcoded credentials in deployment scripts are for demonstration only and not used in production
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The migration will standardize on YAML syntax for all configuration
7. No external data sources or complex variable structures are in use
8. No complex orchestration or multi-server deployments are required