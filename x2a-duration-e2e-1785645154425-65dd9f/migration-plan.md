# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer. The primary challenge will be replacing the Chef Automate/Infra Server deployment with equivalent Ansible automation while preserving the compliance testing capabilities.

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

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
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings
- `chef-and-ansible/index.html`: Sample HTML content for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other configuration management solution
- **Test Kitchen**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Maintain as a compliance testing tool, integrate with Ansible workflows

### Security Considerations

- **SSL Configuration**: The migration must maintain secure SSL/TLS configurations
  - Migration approach: Preserve the SSL protocol restrictions (TLSv1.2) and certificate generation
  
- **SSH Hardening**: Maintain SSH security compliance checks
  - Migration approach: Keep InSpec tests and ensure Ansible configurations meet the same requirements

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Consider AWX/Tower for web UI and role-based access control
  
- **Compliance Testing**: Maintaining compliance validation capabilities
  - Mitigation: Continue using InSpec for testing, integrate with Ansible workflows

- **User/Organization Management**: Replacing Chef's user and organization structure
  - Mitigation: Implement RBAC in Ansible AWX/Tower or use external identity providers

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Update to use Ansible best practices (roles, collections)
   
2. **InSpec Tests** - Low risk, can be preserved
   - Maintain existing InSpec tests
   - Integrate with Ansible testing workflow
   
3. **Chef Deployment Scripts** - Moderate complexity
   - Create Ansible roles to replace Chef Automate/Infra Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. Chef InSpec will continue to be used for compliance testing
3. The deployment environment (Ubuntu 20.04, Vagrant) will remain the same
4. No external dependencies or integrations beyond what's visible in the repository
5. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure alternatives
6. The organization structure defined in the Chef scripts needs to be maintained in some form
7. The repository is primarily for demonstration/example purposes rather than production use