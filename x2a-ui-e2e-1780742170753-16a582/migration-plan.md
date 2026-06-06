# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server functionality. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for infrastructure testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that either:
  - Install and configure open-source alternatives like AWX/Tower
  - Or maintain Chef Automate/Server installation if still required, but managed via Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the Apache configuration:
  - Disable SSLv3 protocol (POODLE vulnerability mitigation)
  - Enable only TLSv1.2 or higher
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: Ensure SSH security controls are maintained:
  - Root login restrictions
  - Proper authentication methods

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username: jtonello, password: password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL key/cert pair)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-compatible testing frameworks will require careful mapping of InSpec resources to Testinfra or Goss syntax.
  - Mitigation: Create a mapping document for InSpec resources to Testinfra/Goss equivalents and validate each test conversion individually.

- **Chef Server Functionality**: If Chef Server functionality is still needed, determine how to maintain it while managing it with Ansible.
  - Mitigation: Evaluate if Chef Server is still required or if it can be replaced entirely with Ansible Tower/AWX.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring to follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing frameworks.

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires decisions about whether to maintain Chef infrastructure or replace it entirely.

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, eliminating Chef where possible.

2. InSpec tests are being used for compliance validation and could potentially be replaced with Ansible-native testing solutions.

3. The Chef Automate and Chef Server deployment scripts may be replaced with equivalent Ansible functionality or with Ansible Tower/AWX deployment.

4. The current setup appears to be a demonstration or testing environment rather than a production system, based on the self-signed certificates and test content.

5. The repository structure suggests this is primarily educational/example content rather than production infrastructure code.

6. No external data sources or complex state management is evident in the current implementation.

7. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in a production environment.