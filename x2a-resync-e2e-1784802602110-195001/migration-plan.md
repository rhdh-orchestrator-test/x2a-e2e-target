# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks that are already in place
3. Maintaining Chef InSpec tests for compliance validation
4. Ensuring proper integration between components

The estimated timeline for migration is 1-2 weeks given the limited scope and the fact that some components are already using Ansible.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file used in website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Chef Server CLI**: Replace with Ansible roles for configuration management server deployment
- **Test Kitchen with Ansible**: Maintain but update configuration to use pure Ansible testing approach
- **InSpec**: Maintain as a compliance testing tool, which works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve the security posture:
  - Self-signed certificates are generated in the website_https.yml playbook
  - POODLE vulnerability remediation in poodle_fix.yml
  
- **SSH Hardening**: SSH security is tested via InSpec but not configured in the playbooks:
  - Maintain the InSpec tests for SSH configuration validation
  - Consider adding explicit SSH hardening to the Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible requires understanding of Chef Automate's architecture and deployment requirements:
  - Need to research available Ansible roles for Chef Automate deployment or create custom roles
  - System requirements (vm.max_map_count, vm.dirty_expire_centisecs) need to be maintained
  - User and organization creation needs to be handled via API calls or CLI commands

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible deployments:
  - Maintain the existing InSpec tests
  - Update Test Kitchen configuration if needed
  - Consider implementing CI/CD pipeline integration

### Migration Order

1. **Existing Ansible Playbooks** (Low risk, already Ansible)
   - Maintain website_https.yml and poodle_fix.yml as they are already in Ansible format
   - Update documentation and comments as needed

2. **Chef Server Deployment** (Medium complexity)
   - Create Ansible playbook to replace deploy-chef-server.sh
   - Implement Ansible Vault for credential storage
   - Test deployment and validate functionality

3. **Chef Automate Deployment** (Higher complexity)
   - Create Ansible playbook to replace deploy-automate.sh
   - Implement Ansible Vault for credential storage
   - Test deployment and validate functionality

4. **Testing Framework** (Low risk, infrastructure support)
   - Update Test Kitchen configuration if needed
   - Ensure InSpec tests are properly integrated with Ansible playbooks
   - Implement CI/CD pipeline for automated testing

### Assumptions

1. The repository is primarily used for demonstration and educational purposes rather than production deployment, based on the README content.
2. The Chef Automate and Chef Infra Server deployment scripts are intended for on-premises or cloud VM deployment.
3. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are functional and follow best practices.
4. InSpec is the preferred compliance testing tool and should be maintained in the migration.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
6. The target environment is Ubuntu 20.04 based on the Test Kitchen configuration.
7. The migration will maintain backward compatibility with existing tests and verification methods.