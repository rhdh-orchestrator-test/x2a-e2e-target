# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with shell scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing primarily on converting existing Ansible playbooks to a more standardized Ansible structure and integrating the Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of playbooks and tests.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require updating to use Ansible-native testing frameworks or adapting to work with pure Ansible.
- `deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Will need to be replaced with Ansible playbooks for infrastructure deployment.
- `deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Will need to be replaced with Ansible playbooks for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Ansible's built-in inventory management for multi-environment testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache security hardening that includes the SSL/TLS configurations
  
- **SSH Security**: The SSH security tests must be preserved
  - Approach: Convert the InSpec SSH tests to Ansible assertions or maintain as InSpec tests run by Ansible

- **Vault/secrets management**:
  - No explicit secrets management was found in the repository
  - The deploy scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions may lose some of the declarative testing capabilities
  - Mitigation: Consider keeping InSpec as a testing tool invoked by Ansible or use Molecule with testinfra

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks
  - Mitigation: Create dedicated Ansible roles for Chef server deployment if still needed, or replace with alternative solutions

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Refactor into proper Ansible role structure
2. **poodle_fix.yml** (low risk, already Ansible): Integrate into the Apache security role
3. **InSpec Tests** (moderate complexity): Convert to Ansible assertions or integrate with Ansible workflow
4. **Deployment Scripts** (high complexity): Convert to Ansible playbooks or replace with alternative solutions

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts are used for setting up test environments and not production systems
4. No external dependencies or inventory files exist beyond what's visible in the repository
5. The Apache configuration is relatively simple and doesn't have complex dependencies
6. The team is familiar with both Chef InSpec and Ansible
7. There's no requirement to maintain backward compatibility with Chef tools