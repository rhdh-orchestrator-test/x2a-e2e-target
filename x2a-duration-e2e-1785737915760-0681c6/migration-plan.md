# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that configure web servers with HTTPS
2. Chef InSpec tests used for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The main work involves converting InSpec tests to Ansible-compatible testing frameworks and updating the deployment scripts to use Ansible roles instead of shell scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Should be migrated to Ansible-compatible testing frameworks like Testinfra or Molecule.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH configuration. Should be migrated to Ansible-compatible testing frameworks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the deployment scripts are designed to work on any cloud or on-premises VM

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
- **InSpec (latest)**: Replace with Ansible-compatible testing frameworks like Testinfra or Molecule's built-in verification
- **Chef Automate/Infra Server**: Consider if these components are still needed or if they can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are enforced in the migrated Ansible roles.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing Let's Encrypt integration for production environments.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Ensure this security check is maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No encrypted data bags or other secret management systems detected

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches and syntax.
  - Mitigation: Use Molecule's built-in verification capabilities or Testinfra, which has a similar syntax to InSpec.
  
- **Chef Automate/Infra Server Deployment**: The shell scripts for deploying Chef infrastructure need to be converted to Ansible roles.
  - Mitigation: Create Ansible roles that perform the same steps as the shell scripts, using Ansible modules for package installation, service configuration, and command execution.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Convert to Ansible role structure
   - Update testing framework

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Convert to Ansible role structure
   - Update testing framework

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing frameworks

4. **Chef deployment scripts** (moderate complexity)
   - Convert to Ansible roles
   - Implement secret management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, as indicated by the README.
2. The Chef InSpec tests are used alongside Ansible for compliance verification, not as part of a larger Chef infrastructure.
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced with Ansible Tower/AWX in the migrated solution.
4. The target environment is Ubuntu 20.04, as specified in the kitchen.yml file.
5. The current implementation uses self-signed certificates for HTTPS, which may not be suitable for production environments.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure secret management in production.