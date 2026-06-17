# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

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
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port checking, HTTP response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts could be used in any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use community.general.assert module for basic testing within Ansible
  - Option 3: Integrate with other testing frameworks like Serverspec or BATS

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning using OpenSCAP or similar tools integrated with Ansible

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task directly to the new Ansible structure

- **SSH Security Controls**: The SSH root login control must be preserved
  - Approach: Convert InSpec test to Ansible assert or Molecule/Testinfra test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing
  - Mitigation: Use Molecule with Testinfra which provides similar functionality to InSpec
  - Consider maintaining some InSpec tests if they provide unique value not easily replicated

- **Compliance Validation**: Ensuring the same level of compliance checking
  - Mitigation: Map InSpec controls to equivalent Ansible checks or OpenSCAP profiles

- **Chef Server Functionality**: Replacing Chef Server management capabilities
  - Mitigation: Document Ansible inventory and collection management practices to replace Chef Server functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible roles for infrastructure setup

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for validation only and not for active compliance monitoring
3. There are no external dependencies on Chef Automate for compliance reporting
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The migration will maintain the same level of security hardening present in the original code
6. No additional Chef cookbooks or resources are used beyond what's visible in the repository
7. The Apache configuration and SSL setup requirements will remain the same after migration