# MIGRATION FROM CHEF AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on two main components:

1. Chef server deployment scripts (Bash)
2. Existing Ansible playbooks with InSpec tests

The migration complexity is **LOW** as most of the content is already in Ansible format or consists of simple Bash scripts that can be easily converted to Ansible roles. The estimated timeline for complete migration is **1-2 weeks** for a single developer.

## Module Migration Plan

This repository contains Ansible playbooks and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration to disable vulnerable protocols

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `chef-and-ansible/index.html`: Sample HTML file for testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Keep InSpec for testing but integrate with Ansible using the ansible_playbook provisioner

- **Test Kitchen (latest)**: Replace with:
  - Option 1: molecule for Ansible role testing
  - Option 2: Keep Test Kitchen with the ansible_playbook provisioner

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL vulnerabilities by enforcing TLSv1.2. This should be incorporated into the main Apache role.
  
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. In production, consider:
  - Using the ansible.builtin.acme_certificate module for Let's Encrypt certificates
  - Implementing certificate management through a dedicated role

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Server Deployment**: The Bash scripts for Chef server deployment need to be converted to Ansible roles. This involves:
  - Creating a role structure for Chef server deployment
  - Converting Bash commands to Ansible modules
  - Implementing proper variable management for configuration
  - Challenge mitigation: Use the ansible.builtin.command module for Chef-specific commands that don't have equivalent Ansible modules

- **InSpec Testing Integration**: Maintaining compliance testing while migrating to Ansible:
  - Challenge: Preserving the compliance testing capabilities of InSpec
  - Mitigation: Either convert InSpec tests to Ansible assertions or maintain InSpec as a testing tool alongside Ansible

### Migration Order

1. **website-https playbook** (already in Ansible format, low risk)
   - Review and refactor into a proper role structure
   - Update SSL configuration to incorporate poodle_fix.yml changes

2. **poodle-fix playbook** (already in Ansible format, low risk)
   - Merge into the Apache/web server role created from website-https.yml

3. **Chef server deployment scripts** (moderate complexity)
   - Convert Bash scripts to Ansible roles
   - Implement proper variable management and secrets handling

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, not production deployments (based on README.md content).
2. The InSpec tests are essential for compliance verification and should be preserved in some form.
3. The Chef server deployment scripts are used for setting up test environments and not for production Chef infrastructure.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.