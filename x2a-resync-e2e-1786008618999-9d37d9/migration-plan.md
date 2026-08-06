# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Ansible playbooks with Chef InSpec tests for compliance automation
2. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as the Ansible components can be directly reused, while the Chef deployment scripts need to be converted to Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with the primary focus on replacing the Chef server deployment scripts with equivalent Ansible roles.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

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
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test profile for verifying HTTPS configuration
- `tests/ssh_profile.rb`: Chef InSpec test profile for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or maintain InSpec as a standalone testing tool
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain as a testing framework
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or equivalent solution

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH security profile in tests/ssh_profile.rb must be implemented in Ansible
- **Self-signed Certificates**: The certificate generation process should be maintained or improved
- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - No other credential patterns detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing may require additional effort
- **Chef Server Functionality**: Ensuring all Chef Server functionality is properly replaced with Ansible equivalents
- **Compliance Automation**: Maintaining the compliance automation capabilities currently provided by InSpec

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. InSpec tests - moderate complexity, convert to Ansible-native testing or maintain as-is
3. Chef deployment scripts - high complexity, requires complete rewrite as Ansible roles

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible for compliance automation
2. The Chef deployment scripts are used for setting up a test environment rather than production infrastructure
3. There are no external dependencies or integrations not visible in the repository
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The repository is intended for educational/demonstration purposes rather than production use