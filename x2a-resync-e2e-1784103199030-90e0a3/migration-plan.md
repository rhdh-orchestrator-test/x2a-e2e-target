# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Sample HTML file used in the website deployment - can be preserved as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Integration with other compliance tools like OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible automation controller (AWX/Tower) or other orchestration tools

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with proper documentation of security implications

- **SSH Security Controls**: The SSH root login compliance check must be preserved
  - Approach: Convert InSpec control to Ansible assert or Molecule/Testinfra test

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Approach: Use Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Testinfra with Molecule which provides similar testing capabilities
  - Challenge: Maintaining the same level of expressiveness and readability in tests

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs equivalent in Ansible
  - Mitigation: Integrate with AWX/Tower reporting or third-party compliance tools

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible-native solutions
  - Mitigation: Use AWX/Tower for orchestration, GitLab/GitHub for code management, and Ansible collections for configuration management

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality with Ansible equivalents

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and follow best practices
2. The InSpec tests are currently used for compliance validation of infrastructure configured by Ansible
3. The repository demonstrates integration between Chef InSpec and Ansible rather than being a production environment
4. The Chef Automate and Chef Infra Server deployment scripts are examples and not part of a larger Chef ecosystem
5. No external dependencies or integrations beyond what's visible in the repository
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
7. The migration will maintain the same level of security compliance as the original implementation
8. No custom InSpec resources are being used beyond what's shown in the test files