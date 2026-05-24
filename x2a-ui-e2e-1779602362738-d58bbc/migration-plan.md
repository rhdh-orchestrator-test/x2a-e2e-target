# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity as most of the configuration is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Static HTML content for the web server. No migration needed as it's content, not configuration.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use the Ansible `assert` module
  - For comprehensive testing: Implement Molecule with Testinfra or Goss
  - For compliance testing: Consider OpenSCAP integration with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Convert to Ansible role with proper SSL configuration
  
- **SSH Security**: The SSH root login check must be preserved
  - Migration approach: Convert InSpec test to Ansible assert or Molecule with Testinfra

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Compliance Testing**: Chef InSpec provides rich compliance testing capabilities
  - Mitigation: Evaluate Ansible-native compliance solutions like OpenSCAP or integrate with cloud provider compliance tools

- **Test Reporting**: InSpec provides structured test reporting
  - Mitigation: Implement custom reporting with Ansible or use Molecule's reporting capabilities

### Migration Order

1. **website_https_verify.rb** (low risk, high value) - Convert to Ansible assert or Molecule tests
2. **ssh_profile.rb** (low risk, high value) - Convert to Ansible assert or Molecule tests
3. **Chef Automate deployment scripts** (moderate complexity) - Convert to Ansible roles for Chef server deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
3. The security compliance requirements (STIG standards referenced in ssh_profile.rb) must be maintained
4. The Chef Automate and Chef Server deployment scripts may still be needed if the organization continues to use Chef for other purposes
5. No specific performance requirements are mentioned for the web server configuration
6. The self-signed certificates are acceptable for the environment (not production)
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only