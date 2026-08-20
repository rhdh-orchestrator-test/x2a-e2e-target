# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and integrating the Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing capabilities or integrate with Ansible using the `ansible.builtin.shell` module to run InSpec tests
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Vagrant**: Can be retained for local testing or replaced with Molecule's containerized testing approach

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with proper templates for SSL configuration
  
- **SSH Security**: The SSH security checks in ssh_profile.rb need to be preserved
  - Approach: Convert InSpec tests to Ansible assert tasks or maintain InSpec tests and run them via Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting Chef InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible assert modules where possible, or maintain InSpec as a testing tool called from Ansible
  
- **Chef Automate Deployment**: Replacing Chef Automate/Infra Server deployment with equivalent Ansible automation
  - Mitigation: Create Ansible roles for configuration management without requiring Chef infrastructure

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Add documentation and parameterization

2. **poodle_fix.yml** (low risk, already Ansible)
   - Integrate with website_https role as a security enhancement
   - Add conditional application based on variables

3. **InSpec Tests** (moderate complexity)
   - Either convert to Ansible assertions or
   - Create an Ansible role to run InSpec tests as part of the deployment pipeline

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible roles for configuration management
   - Implement alternative monitoring and compliance solutions

### Assumptions

1. The primary goal is to consolidate on Ansible as the sole configuration management tool
2. InSpec testing capabilities are still desired, even if the implementation changes
3. The Chef Automate and Chef Infra Server deployments are for demonstration purposes and not critical production infrastructure
4. The existing Ansible playbooks follow older patterns and would benefit from refactoring to roles
5. No external Chef cookbooks or complex Chef-specific features are in use
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. Test Kitchen and Vagrant will be replaced with Ansible Molecule for testing
8. The migration will prioritize maintaining security configurations and testing capabilities