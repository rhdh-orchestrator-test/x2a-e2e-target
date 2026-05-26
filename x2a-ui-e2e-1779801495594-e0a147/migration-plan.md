# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as most of the configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef Server CLI
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef Automate CLI
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Can be preserved as-is or converted to a template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud platform

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for Python-based testing
  - Option 2: Use Ansible assert modules for basic compliance checks
  - Option 3: Integrate with OpenSCAP for more comprehensive compliance testing

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: The deployment scripts can be converted to Ansible playbooks if Chef infrastructure is still needed, or removed if moving entirely to Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with appropriate SSL configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Approach: Convert to Ansible assert task or Molecule Testinfra test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should use Ansible Vault for production environments

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to equivalent Ansible testing solutions
  - Mitigation: Use Ansible Molecule with Testinfra which provides similar testing capabilities

- **Test Kitchen Integration**: Replacing Test Kitchen workflow
  - Mitigation: Implement Ansible Molecule for testing with similar capabilities

### Migration Order

1. Convert Chef InSpec tests to Ansible Molecule/Testinfra tests (low risk, preserves functionality)
2. Update existing Ansible playbooks to use Ansible best practices (moderate complexity)
3. Convert Chef Server/Automate deployment scripts to Ansible playbooks (if needed)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The existing Ansible playbooks are functional and don't require significant changes
3. The Chef Server/Automate deployment scripts may not be needed if moving entirely to Ansible
4. No external Chef cookbooks or complex Chef-specific features are being used
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only