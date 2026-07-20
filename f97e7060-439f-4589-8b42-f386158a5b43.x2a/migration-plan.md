# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, primarily involving Chef Automate and Chef Infra Server deployment scripts, along with InSpec test profiles that are already designed to work with Ansible. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already Ansible-compatible or are simple deployment scripts.

## Module Migration Plan

This repository contains Chef deployment scripts and InSpec test profiles that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, server configuration, automated deployment of Chef infrastructure
    - Files:
      - deploy-automate.sh: Deploys both Chef Automate and Chef Infra Server
      - deploy-chef-server.sh: Deploys only Chef Infra Server

- **inspec-compliance-profiles**:
    - Description: Chef InSpec profiles for testing compliance of web servers and SSH configurations
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol testing, SSH security compliance checks
    - Files:
      - website_https_verify.rb: Tests for proper HTTPS configuration and TLS protocols
      - ssh_profile.rb: Tests for secure SSH configuration (disabled root login)

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server with HTTPS support. No migration needed as it's already in Ansible format.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache. No migration needed as it's already in Ansible format.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Will need to be updated to use pure Ansible testing framework.
- `chef-and-ansible/index.html`: Sample HTML file used in the web server deployment. No migration needed.

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with support for both on-premises and cloud deployments (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Can be retained as a compliance testing tool that works with Ansible, or replaced with Ansible-native solutions like:
  - ansible-lint for static code analysis
  - Molecule for Ansible role testing
  - OpenSCAP integration for compliance scanning

### Security Considerations

- **SSH Configuration**: The InSpec profile tests for secure SSH configuration (disabled root login). Migration should ensure equivalent Ansible tasks to enforce this security practice.
- **SSL/TLS Configuration**: The InSpec profile and Ansible playbooks enforce TLS 1.2 and disable insecure protocols. Migration should maintain these security controls.
- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the Ansible playbook and should be handled securely in the migrated solution

### Technical Challenges

- **Chef InSpec Integration**: While InSpec works well with Ansible, teams may prefer a pure Ansible solution. Consider whether to maintain InSpec for compliance testing or migrate to Ansible-native testing tools.
- **Deployment Automation**: The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible roles and playbooks, which will require understanding of the Chef server architecture.

### Migration Order

1. Chef deployment scripts (setup-automate/*.sh) - Convert to Ansible roles and playbooks
2. Test Kitchen configuration (chef-and-ansible/kitchen.yml) - Update to use Ansible-native testing framework
3. InSpec profiles (optional) - Consider whether to keep as-is or migrate to Ansible-native testing

### Assumptions

1. The repository is primarily a demonstration of how Chef InSpec can work alongside Ansible, rather than a production deployment.
2. The Ansible playbooks (website_https.yml, poodle_fix.yml) are already in the target format and don't need migration.
3. The deployment scripts are used for setting up Chef infrastructure, which may not be needed after migration to Ansible.
4. The InSpec profiles are valuable for compliance testing and could be retained even after migration to Ansible.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
6. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.