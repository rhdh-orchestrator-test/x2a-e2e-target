# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef-related deployment scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, as indicated by the README files. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts for Chef server deployment. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs as mentioned in script comments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks like Molecule with TestInfra or maintain InSpec as a standalone testing tool
- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible-compatible management solutions

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve the security posture:
  - Ensure continued disabling of SSLv3 (POODLE vulnerability mitigation)
  - Enforce TLSv1.2 or higher
  - Maintain proper certificate generation and management

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure root login remains disabled
  - Maintain SSH security controls during migration

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in the website_https.yml playbook
  - Recommend replacing with Ansible Vault or external secrets management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to TestInfra or other Ansible-compatible testing frameworks
  - Mitigation: Create equivalent tests in TestInfra or maintain InSpec as a standalone testing tool

- **Chef Server Deployment**: Replacing Chef Server deployment scripts with equivalent Ansible roles
  - Mitigation: Create Ansible roles for configuration management server deployment or integrate with existing Ansible Automation Platform

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role for better reusability

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Integrate with the website-https role as a security hardening task
   - Ensure idempotence and proper testing

3. **InSpec tests** (moderate complexity)
   - Convert to TestInfra or maintain as standalone tests
   - Ensure test coverage remains comprehensive

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles for deploying configuration management tools
   - Implement proper secret management for credentials

### Assumptions

1. The repository is primarily for demonstration purposes, as indicated by the README files
2. The Chef components are intended to be replaced with Ansible equivalents
3. InSpec testing is a key requirement that should be maintained or replaced with equivalent functionality
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The security configurations (SSL/TLS, SSH) are critical and must be maintained
6. The hardcoded credentials in the scripts are for demonstration only and will be replaced with proper secret management