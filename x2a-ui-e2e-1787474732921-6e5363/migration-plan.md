# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains examples of Chef InSpec with Ansible and Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on:

1. Ansible playbooks that deploy a web server with HTTPS configuration
2. Chef InSpec tests for compliance verification
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on:
- Converting Chef InSpec tests to Ansible-compatible testing frameworks
- Enhancing the existing Ansible playbooks
- Converting Chef Automate/Infra Server deployment scripts to Ansible roles

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML content for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for playbook verification
  - Option 3: Continue using InSpec but integrate with Ansible workflow

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible Test for playbook verification

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for CI/CD pipeline integration

### Security Considerations

- **SSL Configuration**: The current playbooks configure SSL with self-signed certificates. Migration should:
  - Maintain or improve the TLS protocol security (currently enforcing TLS 1.2)
  - Consider adding support for Let's Encrypt for production environments
  - Implement proper certificate management

- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials:
  - In `deploy-automate.sh` and `deploy-chef-server.sh`, replace hardcoded passwords with Ansible Vault
  - Implement secure variable handling for sensitive information

- **Vault/secrets management**:
  - No encrypted data bags or Chef Vault usage detected
  - 1 hardcoded password in each deployment script
  - SSL certificate references in the Ansible playbooks should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework:
  - Challenge: InSpec has specific syntax for compliance testing
  - Mitigation: Use Molecule with Testinfra or maintain InSpec as a separate testing tool

- **Chef Automate/Infra Server Deployment**: Converting deployment scripts to Ansible:
  - Challenge: Ensuring all Chef server configuration is properly translated
  - Mitigation: Create dedicated Ansible roles for Chef server deployment or replace with Ansible Automation Platform

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and enhance the existing Ansible playbook
   - Add idempotence improvements
   - Implement Ansible best practices

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and enhance the existing Ansible playbook
   - Consider merging with website_https as a single role

3. **InSpec tests** (moderate complexity)
   - Convert to Molecule/Testinfra or maintain as separate InSpec tests
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for Chef server deployment
   - Or replace with Ansible Automation Platform deployment

### Assumptions

1. The repository is primarily for demonstration purposes, not production use
2. The InSpec tests are essential for compliance verification and must be preserved in some form
3. The deployment scripts are examples and may not reflect actual production deployment requirements
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The migration will maintain the same functionality but improve maintainability and follow Ansible best practices
6. No external dependencies or inventory files are present in the repository
7. The Apache configuration in the playbooks is basic and doesn't include complex configurations
8. The self-signed certificates are for demonstration purposes and would be replaced in production