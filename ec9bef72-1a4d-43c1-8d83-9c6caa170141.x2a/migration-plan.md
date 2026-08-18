# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and shell scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test profile for verifying SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec (latest)**: Can be retained as Ansible can still use InSpec for compliance testing, or migrate to Ansible's built-in assert module for basic tests
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that install and configure equivalent monitoring and compliance tools

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Maintain proper certificate generation and management
  
- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Ensure root login remains disabled
  - Maintain SSH security best practices in the migrated solution

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be migrated to Ansible Vault or another secure secrets management solution

### Technical Challenges

- **InSpec Integration**: The current setup uses InSpec for compliance testing with Ansible. The migration should:
  - Either maintain InSpec integration with Ansible
  - Or replace InSpec tests with equivalent Ansible testing mechanisms
  
- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality:
  - Consider AWX/Ansible Tower for web UI and job scheduling
  - Implement equivalent compliance reporting mechanisms

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Update to use Ansible best practices and idempotent modules

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Integrate with the website_https playbook if appropriate

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement secure credential management using Ansible Vault

4. **Testing Framework** (moderate complexity)
   - Migrate from Test Kitchen to Ansible Molecule
   - Adapt or convert InSpec tests to work with the new testing framework

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool
2. InSpec testing capabilities are still desired, even after migration to Ansible
3. The Chef Automate and Chef Infra Server deployments need to be replaced with equivalent functionality
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions
5. Vagrant will continue to be used for local development and testing
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution