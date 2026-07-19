# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec tests that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **2-3 weeks** for a small team (1-2 engineers). The primary challenge will be replacing Chef InSpec testing with equivalent Ansible testing solutions while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, disabling SSLv3

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for validating HTTPS website and SSH configuration
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL protocol verification, SSH security compliance checks

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file used for testing the web server deployment. Can be retained as-is or moved to a templates directory in the Ansible structure.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for advanced compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing and verification

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older SSL/TLS protocols
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH compliance profile (ssh_profile.rb) checks for root login restrictions:
  - Ensure this security check is maintained in the migrated solution
  - Consider expanding SSH hardening based on the CIS benchmarks referenced in the InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend replacing with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Replacing Chef InSpec with equivalent Ansible testing solutions while maintaining the same level of compliance validation:
  - InSpec provides specialized resources for testing SSL/TLS configurations
  - Need to identify or develop equivalent testing capabilities in Ansible

- **Certificate Management**: The current solution generates self-signed certificates:
  - Consider enhancing with Let's Encrypt integration for production environments
  - Ensure proper certificate rotation and management

### Migration Order

1. **apache-https-website** (low risk, already in Ansible): Standardize the existing Ansible playbook to follow best practices
2. **ssl-poodle-fix** (low risk, already in Ansible): Integrate with the apache-https-website playbook as a role
3. **chef-automate-deployment** (medium complexity): Convert Bash scripts to Ansible playbooks
4. **inspec-compliance-tests** (high complexity): Replace with Ansible-native testing solutions

### Assumptions

1. The repository is primarily used for demonstration and educational purposes, as indicated by the README.md mentioning "working examples" and "companion to a white paper."
2. The Chef InSpec tests are intended to validate compliance of systems managed by Ansible, not Chef-managed systems.
3. The deployment scripts contain default/example values that would need to be parameterized in a production environment.
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
5. The current implementation uses self-signed certificates, which may need to be replaced with proper CA-signed certificates in production.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would need to be secured in a production environment.