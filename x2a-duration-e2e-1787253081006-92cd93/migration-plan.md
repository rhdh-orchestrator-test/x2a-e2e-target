# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment with Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Migrating existing Ansible playbooks to a standardized Ansible structure
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible automation

Given the limited scope and small number of components, this migration is estimated to be **low complexity** with an estimated timeline of **1-2 weeks** for a single engineer.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef components that need individual migration planning:

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

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Static HTML content for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for Ansible content management
  - Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The existing playbooks configure SSL for Apache. Migration should:
  - Update SSL protocols to current best practices (TLS 1.3 support)
  - Use Ansible Vault for storing sensitive information
  - Consider using Let's Encrypt for certificate management instead of self-signed certificates

- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Use environment variables or external secret management systems

- **Vault/secrets management**:
  - No encrypted secrets were found in the current repository
  - 2 instances of hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Solution: Use Ansible assert modules or Molecule verifiers to replicate InSpec tests

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents:
  - Solution: Use AWX/Ansible Tower for web UI and job scheduling
  - Solution: Use Git repositories for content management
  - Solution: Use Ansible Collections for sharing reusable content

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, already in Ansible format
   - Refactor to follow Ansible best practices (roles, collections)

2. **InSpec Tests** (website_https_verify.rb):
   - Moderate complexity
   - Convert to Ansible Molecule tests or ansible-test framework

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Higher complexity
   - Create Ansible playbooks to replace Chef Automate/Infra Server or deploy alternative solutions

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production workloads
2. No external dependencies or integrations beyond what's visible in the repository
3. No complex data migration requirements from Chef to Ansible
4. The team has basic Ansible knowledge and can adapt to Ansible-based testing frameworks
5. The Apache configuration requirements will remain the same after migration
6. The Chef InSpec tests are only used for the specific website HTTPS verification and not part of a larger compliance framework
7. The deployment scripts are used for standalone Chef environments and not integrated with other systems