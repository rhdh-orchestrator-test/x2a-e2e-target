# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as the Ansible components are already in place.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with SSL/TLS for a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML content for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing similar to InSpec, evaluate options like:
    - Ansible Molecule with testinfra backend
    - OpenSCAP with Ansible integration
    - Ansible's assert module for basic compliance checks

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Molecule already supports multiple drivers including Vagrant

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSL protocol restrictions are maintained (disabling SSLv3, enabling TLSv1.2)
  - Maintain the same security posture in the Apache configuration

- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login being disabled
  - Create equivalent checks in the Ansible testing framework
  - Consider adding an Ansible task to enforce this configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (deploy-automate.sh, deploy-chef-server.sh)
    - Replace with Ansible Vault for secure credential storage
  - Self-signed certificates in website_https.yml
    - Consider using Ansible Vault for storing private keys
    - Evaluate using Let's Encrypt for production environments

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: Maintaining the same level of test coverage and readability
  - Mitigation: Map InSpec resources to equivalent testinfra or Molecule verifiers

- **Compliance Validation**: Ensuring the same compliance checks are performed
  - Challenge: InSpec is purpose-built for compliance testing
  - Mitigation: Evaluate compliance-focused Ansible collections or integrate with OpenSCAP

- **Chef Automate/Server Deployment**: Converting bash scripts to Ansible playbooks
  - Challenge: Ensuring idempotent execution and proper error handling
  - Mitigation: Break down the script into discrete Ansible tasks with proper conditionals

### Migration Order

1. **InSpec Tests** (chef-and-ansible/tests/*.rb)
   - Convert to Ansible Molecule tests first to establish testing framework
   - Low risk as they don't modify production systems

2. **Test Kitchen Configuration** (chef-and-ansible/kitchen.yml)
   - Replace with Molecule configuration
   - Moderate complexity due to driver and provisioner settings

3. **Chef Deployment Scripts** (setup-automate/*.sh)
   - Convert to Ansible playbooks
   - Higher complexity due to stateful operations and potential for errors

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README description.
2. The InSpec tests are used for validation only and not for remediation.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
4. The target environment is Ubuntu 20.04 as specified in kitchen.yml.
5. The Apache configuration is relatively simple and focused on SSL/TLS security.
6. The migration will maintain the same level of security validation currently provided by InSpec.
7. No external Chef cookbooks or complex Chef resources are being used that would require significant refactoring.