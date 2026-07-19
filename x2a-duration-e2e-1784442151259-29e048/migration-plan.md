# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the codebase is small and well-structured. The main challenge will be ensuring proper integration of compliance testing within the Ansible framework.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML file for website deployment
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Integrate with Ansible using one of these approaches:
  1. Use ansible-lint for basic compliance checks
  2. Use Ansible's built-in assert module for simple tests
  3. Maintain InSpec for complex compliance testing, called from Ansible
  4. Migrate to Ansible Automation Platform with built-in compliance capabilities

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
- **SSH Security**: The SSH root login compliance check must be preserved in the Ansible framework
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider integrating with Let's Encrypt for production
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificate and key files generated and stored in /etc/apache2/certs

### Technical Challenges

- **InSpec Integration**: Determining the best approach to maintain compliance testing within an Ansible-only framework
- **Chef Automate Replacement**: Identifying the appropriate Ansible components to replace Chef Automate functionality
- **Test Kitchen**: Replacing Test Kitchen with Ansible-native testing frameworks like Molecule

### Migration Order

1. **apache-https-website** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Update to follow Ansible best practices (roles, variables)

2. **ssl-poodle-fix** (low risk, already in Ansible)
   - Integrate with the apache-https-website role
   - Ensure idempotency and proper handlers

3. **inspec-compliance-tests** (medium complexity)
   - Decide on compliance testing strategy
   - Implement chosen approach (ansible-lint, assert, or maintain InSpec)

4. **chef-automate-deployment** (high complexity)
   - Create Ansible roles for Chef Automate functionality
   - Implement user and organization management in Ansible

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. InSpec tests can be replaced with equivalent Ansible testing mechanisms
3. The deployment scripts are for development/testing environments (given the hardcoded credentials)
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The migration does not need to address scaling or high-availability concerns (not present in the original code)
7. The security compliance requirements represented by the InSpec tests must be maintained in the migrated solution