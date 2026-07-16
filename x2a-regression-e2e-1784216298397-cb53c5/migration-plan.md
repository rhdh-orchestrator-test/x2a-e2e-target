# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully migrate all components to pure Ansible. The primary focus will be on replacing Chef InSpec tests with equivalent Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificates, and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol validation, SSH root login security check

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration will require replacing with Ansible-native testing framework.
- `index.html`: Simple HTML file used as a test website. Can be preserved as-is or converted to a template.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Integration with other compliance tools like Ansible Lint or OpenSCAP

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: The deployment scripts should be replaced with:
  - Ansible playbooks for infrastructure deployment
  - Consider migrating to Ansible Tower/AWX for enterprise management capabilities

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains enforced
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH root login restrictions verified by the InSpec tests
  - Implement equivalent Ansible tasks to enforce SSH security configurations
  - Add Ansible-native verification of SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Migration should implement Ansible Vault for secure credential storage
  - Replace plaintext passwords in scripts with secure variable handling

### Technical Challenges

- **InSpec Test Conversion**: Converting Chef InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible assert modules or custom modules to perform equivalent checks
  - Consider implementing Ansible callback plugins for compliance reporting

- **Test Kitchen Replacement**: Finding equivalent functionality in Molecule or other Ansible testing frameworks
  - Mitigation: Create Molecule scenarios that replicate the Test Kitchen configurations

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible management solution
  - Mitigation: Document transition path from Chef Server to Ansible Tower/AWX or alternative

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and variable improvements

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https-configuration as a role

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible-native testing
   - Implement equivalent assertions and checks

4. **chef-server-deployment** (high complexity)
   - Replace with Ansible playbooks for infrastructure management
   - Document transition path from Chef to Ansible

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are critical for compliance verification and must be preserved in functionality
3. The Chef server deployment scripts are used for setting up test environments and not production infrastructure
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. No external dependencies or integrations beyond what's visible in the repository
6. No custom Chef resources or complex Chef-specific functionality that would require special handling