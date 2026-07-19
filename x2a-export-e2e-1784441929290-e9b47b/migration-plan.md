# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate/Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository primarily contains deployment scripts and simple Ansible playbooks with InSpec tests rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **secure-web-server**:
    - Description: Ansible playbook for deploying a secure HTTPS web server with Apache
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec testing
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration, security hardening

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for web server testing
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
  - Migration strategy: Create an Ansible role that performs the same system configurations and deployments as the Chef Automate CLI
  
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to ansible-lint for static analysis
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Integrate with other compliance tools like OVAL or OpenSCAP

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3 (POODLE vulnerability fix)
  - Migration approach: Maintain the same security configurations in Ansible roles
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create an Ansible role for SSH hardening with equivalent checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage
  - Credential count: 5 credentials detected in setup-automate scripts (username, longusername, useremail, userpassword, orgname)

### Technical Challenges

- **Challenge 1**: Replacing Chef InSpec testing with Ansible-native solutions
  - Mitigation: Evaluate Molecule for testing or maintain InSpec as a separate tool if needed
  
- **Challenge 2**: Ensuring equivalent security compliance without InSpec
  - Mitigation: Create comprehensive Ansible roles with built-in compliance checks
  
- **Challenge 3**: Replicating Chef Automate deployment functionality
  - Mitigation: Research available Ansible Galaxy roles for similar functionality or create custom roles

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `chef-and-ansible/website_https.yml` and `chef-and-ansible/poodle_fix.yml` to proper Ansible roles
   - Update testing framework from InSpec to Ansible-native testing

2. **Chef Deployment Scripts** (Medium complexity)
   - Convert `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh` to Ansible roles
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced entirely, rather than maintaining Chef infrastructure alongside Ansible.

3. The InSpec tests are valuable for compliance verification and should be preserved in some form, either through equivalent Ansible checks or by maintaining InSpec as a separate tool.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.

5. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration, but the solution should be adaptable to other Linux distributions.

6. The existing Ansible playbooks in the chef-and-ansible directory are intended to be refactored into proper Ansible roles rather than maintained as standalone playbooks.