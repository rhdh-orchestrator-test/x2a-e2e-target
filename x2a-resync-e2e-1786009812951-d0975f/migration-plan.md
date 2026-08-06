# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on:

1. Consolidating existing Ansible playbooks into a standardized Ansible structure
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

The repository appears to be primarily for demonstration purposes, showing how Chef InSpec can be used alongside Ansible for compliance automation. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
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
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing
- **Chef InSpec**: Can be retained as a testing tool or replaced with Ansible's built-in assert module and community.general collection modules
- **Vagrant**: Can be retained for local testing or replaced with Docker for lighter-weight testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suites
  - Consider adding HSTS headers

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated on the fly but could be pre-generated and stored securely

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef Automate and Chef Infra Server installation
  - Implementing idempotent installation checks
  - Handling certificate and key generation
  - Managing system requirements (vm.max_map_count, vm.dirty_expire_centisecs)

- **InSpec Integration**: Ensuring that InSpec tests can still be run as part of the Ansible workflow:
  - Consider using the `community.general.inspec` module
  - Alternatively, use Ansible's built-in testing capabilities

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Refactor into proper Ansible role structure
   - Improve variable handling
   - Add documentation

2. **poodle_fix playbook** (low risk, already Ansible)
   - Incorporate into the website_https role as a task
   - Add conditional logic for applying the fix

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server
   - Implement secure credential handling with Ansible Vault
   - Add proper error handling and idempotence

### Assumptions

1. The repository is primarily for demonstration purposes and not a production deployment
2. The InSpec tests are intended to be run against Ansible-managed systems
3. The Chef deployment scripts are intended for setting up Chef infrastructure, not for managing application configurations
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The migration should maintain the ability to use InSpec for compliance testing
7. No specific performance requirements are mentioned for the deployed services
8. No specific backup or disaster recovery requirements are mentioned