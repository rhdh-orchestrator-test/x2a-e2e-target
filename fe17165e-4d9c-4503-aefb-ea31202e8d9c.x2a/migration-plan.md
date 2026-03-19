# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec with Ansible for compliance automation. The migration scope is relatively small, consisting primarily of Ansible playbooks with Chef InSpec tests, and Chef Automate/Chef Infra Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file used in the website deployment example
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Maintain InSpec as a separate tool called from Ansible for complex compliance scenarios

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS protocols
  - Approach: Use Ansible's `lineinfile` or `template` modules to configure Apache SSL settings
  
- **SSH Security**: Maintain SSH hardening configurations
  - Approach: Use Ansible's `lineinfile` or dedicated SSH modules to enforce secure SSH configurations

- **Self-signed Certificates**: Maintain the certificate generation process
  - Approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbook

### Technical Challenges

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be replaced with equivalent Ansible functionality
  - Mitigation: Create Ansible roles for deploying alternative compliance and infrastructure management tools like AWX/Ansible Tower

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions or other testing frameworks
  - Mitigation: Create equivalent tests using Ansible's assert module or Molecule verification

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https role as a security hardening task

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are maintained

4. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for deploying alternative infrastructure management tools
   - Consider AWX/Ansible Tower deployment playbooks as replacements

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The Chef Automate and Chef Infra Server deployment is not critical to maintain in the migration
3. The compliance testing functionality provided by InSpec is the most important aspect to preserve
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No secrets management system is currently in use (passwords are hardcoded in scripts)