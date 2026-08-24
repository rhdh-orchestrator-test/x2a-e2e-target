# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The migration scope is minimal, as the repository primarily contains Ansible playbooks that need to be updated rather than converted from another IaC technology. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server.

The migration complexity is low, with an estimated timeline of 1-2 days to update the existing Ansible playbooks to follow modern Ansible best practices and to integrate them with a proper Ansible project structure.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Can be retained as a testing framework or replaced with Ansible's built-in assert module and/or Molecule verifiers
- **Chef Automate/Infra Server**: Consider migrating to Ansible Tower/AWX for enterprise automation platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure modern SSL/TLS protocols are used (already addressed in poodle_fix.yml)
- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider using Let's Encrypt for production
- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained
- **Hardcoded Credentials**: The Chef server deployment scripts contain hardcoded credentials that should be moved to Ansible Vault:
  - Username: jtonello
  - Password: password (insecure)
  - Email: jtonello@chef.lab

### Technical Challenges

- **InSpec Integration**: Determining how to maintain compliance testing with InSpec or migrate to native Ansible testing
- **Chef Server Deployment**: Converting the bash scripts for Chef server deployment to Ansible playbooks if Chef infrastructure is still needed
- **Testing Framework**: Migrating from Test Kitchen to Molecule or another Ansible-native testing framework

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Update to follow modern Ansible best practices
   - Convert to a proper Ansible role structure
   
2. **poodle_fix.yml** (low risk, already Ansible)
   - Update to follow modern Ansible best practices
   - Consider merging with website_https role as a security task
   
3. **InSpec Tests** (moderate complexity)
   - Either maintain as-is with Ansible integration
   - Or convert to Ansible assert tasks or Molecule verifiers
   
4. **Chef Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks if Chef infrastructure is still needed
   - Implement Ansible Vault for credential storage

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are valuable and should be maintained in some form
3. The Chef server deployment scripts may or may not be needed in the future Ansible environment
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The hardcoded credentials in the deployment scripts are for demonstration only and not used in production
6. The self-signed certificates are for testing only and would be replaced with proper certificates in production