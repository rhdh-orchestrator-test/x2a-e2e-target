# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing files and Ansible playbooks that are used for demonstration purposes related to compliance automation. The repository appears to be a set of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for verifying configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration. The main work will involve converting InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier
- `README.md`: Documentation explaining the purpose of the examples
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Maintain InSpec as a standalone testing tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Molecule for Ansible role testing
  - Option 2: Create custom Ansible playbooks for test environment provisioning

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Maintain the same level of Apache security configuration

- **SSH Hardening**: The SSH security tests must be preserved
  - Convert the InSpec SSH tests to equivalent Ansible-compatible tests
  - Ensure root login remains disabled as per compliance requirements

- **Vault/secrets management**:
  - No encrypted secrets were found in the repository
  - Plain text passwords are used in the Chef deployment scripts (userpassword='password')
  - Migration should implement Ansible Vault for securing these credentials

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has specific testing syntax and compliance reporting features
  - Mitigation: Use Ansible Molecule with Testinfra or maintain InSpec as a standalone tool

- **Compliance Reporting**: Maintaining compliance reporting capabilities
  - Challenge: InSpec provides rich compliance reporting that may not be directly available in Ansible
  - Mitigation: Integrate with tools like Ansible Tower/AWX for reporting or maintain InSpec for this purpose

- **Chef Automate Deployment**: Replacing Chef Automate functionality
  - Challenge: The scripts deploy Chef Automate which provides specific compliance and management features
  - Mitigation: Evaluate Ansible Tower/AWX as a replacement or integrate with other compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and optimize existing playbooks
   - Add documentation and improve variable naming

2. **Testing Framework** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert InSpec tests to Ansible Molecule with Testinfra
   - Ensure all compliance checks are preserved

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks for infrastructure deployment
   - Implement Ansible Vault for credential management
   - Consider Ansible Tower/AWX as a replacement for Chef Automate functionality

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The InSpec tests are used for compliance verification of configurations managed by Ansible
3. The deployment scripts are examples and not used in production environments
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or environment-specific configurations are in use
7. The migration will maintain the same level of security and compliance checking
8. The passwords in the deployment scripts are examples and not actual credentials