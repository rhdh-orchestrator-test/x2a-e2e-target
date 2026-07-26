# MIGRATION FROM ANSIBLE AND CHEF SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef-related bash scripts that need to be migrated to a unified Ansible structure. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to convert. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in Ansible format) and medium complexity for the Chef deployment scripts (need conversion to Ansible roles).

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or another Ansible-based configuration management solution

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **POODLE Vulnerability Fix**: The poodle_fix.yml playbook addresses a specific SSL vulnerability. This security hardening must be preserved.
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be replaced with Ansible Vault or another secure secret management solution:
  - Username/password in deploy-automate.sh
  - Username/password in deploy-chef-server.sh

### Technical Challenges

- **Chef InSpec Tests**: Converting Chef InSpec tests to equivalent Ansible testing framework or Molecule tests
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible roles that can deploy alternative configuration management solutions
- **Integration Testing**: Ensuring that the testing framework works correctly with the migrated Ansible roles

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
2. **poodle_fix playbook** (low risk, already in Ansible format)
3. **InSpec tests** (medium complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible roles)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible, not to provide production-ready infrastructure code.
2. The Chef deployment scripts are intended for demonstration purposes and not for production use, given the hardcoded credentials.
3. The target environment for the migrated code will continue to be Ubuntu 20.04 or similar Linux distributions.
4. The migration will need to replace Chef InSpec with an equivalent Ansible-based testing solution.
5. The Chef Automate and Chef Infra Server deployment scripts will need to be replaced with equivalent Ansible roles that deploy alternative configuration management solutions.