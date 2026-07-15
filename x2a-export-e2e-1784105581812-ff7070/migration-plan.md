# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also includes Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
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
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for integration testing
  - Option 3: Continue using InSpec but invoke it from Ansible rather than Test Kitchen

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline integration
  - Compliance scanning tools like OpenSCAP or Ansible's built-in compliance capabilities

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the InSpec tests to equivalent Ansible assertions or Molecule/Testinfra tests

- **SSH Hardening**: The SSH root login check must be maintained
  - Approach: Convert the InSpec control to an Ansible assertion or Molecule/Testinfra test

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, possibly using Ansible Vault or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to equivalent Ansible testing frameworks
  - Mitigation: Use Testinfra with Molecule which provides similar functionality to InSpec

- **Chef Server Functionality**: Replacing Chef Server's organization and user management
  - Mitigation: Use Ansible AWX/Tower for role-based access control and inventory management

- **Compliance Reporting**: Replacing Chef InSpec's compliance reporting capabilities
  - Mitigation: Integrate with tools like OpenSCAP or Ansible's compliance capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Molecule/Testinfra tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for infrastructure setup

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for validation only and not for active remediation
3. There are no external dependencies on Chef Automate's reporting capabilities
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. There are no additional Chef cookbooks or resources not visible in the repository structure
7. The migration will maintain the same level of security compliance checking
8. Test Kitchen is only used for local testing and not in CI/CD pipelines