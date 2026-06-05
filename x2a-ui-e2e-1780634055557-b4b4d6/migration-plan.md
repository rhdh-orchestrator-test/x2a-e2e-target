# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website is properly configured and accessible
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
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used in the website deployment. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Lint for static analysis
  - Option 3: ansible-test for integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Collections for configuration management
  - Compliance as Code frameworks like OpenSCAP or DISA STIG Ansible roles

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with proper SSL configuration templates
  
- **SSH Hardening**: The SSH security controls in ssh_profile.rb need to be implemented as Ansible tasks
  - Approach: Create an Ansible role for SSH hardening with the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Molecule with testinfra which provides similar testing capabilities
  
- **Compliance Reporting**: InSpec provides rich compliance reporting that needs equivalent in Ansible
  - Mitigation: Integrate with OpenSCAP or other compliance tools that can generate reports

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Use Ansible Tower/AWX for centralized management and reporting

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. InSpec tests (website_https_verify.rb, ssh_profile.rb) - Convert to Molecule/testinfra tests
3. Chef deployment scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles

### Assumptions

1. The current setup is used primarily for demonstration purposes rather than production, as indicated by the README.md mentioning these are examples for a white paper.
2. The InSpec tests are used for validation only and not for continuous compliance monitoring.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The migration does not need to preserve Chef Automate functionality but rather replace it with equivalent Ansible capabilities.
6. The self-signed certificates in the website_https.yml playbook are acceptable for the use case and don't need to be replaced with trusted certificates.