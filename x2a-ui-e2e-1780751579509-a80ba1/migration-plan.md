# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security of the Apache web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation with security tags (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis and best practices enforcement

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in inventory management for multi-environment testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for enterprise automation platform
  - GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Maintain the same configuration parameters in the Ansible playbooks
  
- **SSH Security Controls**: The SSH root login verification must be preserved
  - Approach: Convert the InSpec control to Ansible assert tasks or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent
  
- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI numbers) that needs preservation
  - Mitigation: Use Ansible task tags and documentation to preserve compliance metadata

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Mitigation: Research Ansible roles for AWX/Tower deployment or create custom roles based on the installation procedures

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Action: Review and optimize according to current Ansible best practices
   
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Action: Convert to Ansible assert tasks or Molecule tests
   
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Action: Create Ansible roles for AWX/Tower deployment or equivalent CI/CD automation

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require functional changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The security requirements represented in the InSpec tests must be preserved in the migrated solution
4. The deployment scripts are used for setting up a test/demo environment rather than production
5. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository
6. The migration doesn't require preserving Test Kitchen as the testing framework
7. The hardcoded credentials in the deployment scripts are not used in production environments
8. The self-signed certificates are acceptable for the target environment (not requiring trusted CA certificates)